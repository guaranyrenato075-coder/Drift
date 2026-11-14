import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from models.scene_plan import ProjectPlan, Scene, SceneState
from editing.drift_mcp_client import DriftMcpClient
from editing.captions import CaptionManager

class TimelineBuilder:
    """
    Builds and arranges an editable timeline inside Drift via MCP operations.
    """

    def __init__(self, mcp_client: DriftMcpClient):
        self.client = mcp_client

    def build_timeline(self, plan: ProjectPlan) -> Dict[str, Any]:
        """
        Executes the full timeline assembly:
        1. Configures project canvas dimensions and FPS.
        2. Imports audio narration files and video clip files into the media bin.
        3. Sets up tracks: Video lane (0) and Audio lane (1).
        4. Places narration audio clips sequentially.
        5. Places video clips at matched timings and silences background video audio.
        6. Adds subtitle lane with synchronized cues (if enabled).
        7. Returns the build summary.
        """
        # Ensure scenes timings are reindexed
        plan.reindex_scenes()

        # Step 1: Configure project canvas
        self.client.apply([{
            "tool": "set_project_setup",
            "args": {
                "width": plan.config.width,
                "height": plan.config.height,
                "fps": plan.config.fps
            }
        }])

        # Step 2: Collect absolute paths to import
        paths_to_import: List[str] = []
        for s in plan.scenes:
            if s.audio_path and os.path.exists(s.audio_path):
                abs_audio = str(Path(s.audio_path).resolve())
                if abs_audio not in paths_to_import:
                    paths_to_import.append(abs_audio)

            if s.selected_media and s.selected_media.local_cached_path:
                loc = s.selected_media.local_cached_path
                if os.path.exists(loc):
                    abs_vid = str(Path(loc).resolve())
                    if abs_vid not in paths_to_import:
                        paths_to_import.append(abs_vid)

        imported_assets: Dict[str, Any] = {}
        if paths_to_import:
            import_res = self.client.apply([{
                "tool": "import_media",
                "args": {"paths": paths_to_import}
            }])
            done = import_res.get("done", [])
            if done and "result" in done[0]:
                for asset in done[0]["result"].get("assets", []):
                    # Map both name and file path to asset id
                    imported_assets[asset.get("name", "")] = asset.get("id")
                    imported_assets[str(asset.get("id"))] = asset.get("id")

        # Step 3: Ensure we have video and audio tracks with verified indices
        ins = self.client.inspect(clips=False)
        tracks = ins.get("tracks", [])
        has_video_track = any(t.get("type") == "video" for t in tracks)
        has_audio_track = any(t.get("type") == "audio" for t in tracks)

        if not has_video_track:
            self.client.apply([{"tool": "add_track", "args": {"type": "video"}}])
        if not has_audio_track:
            self.client.apply([{"tool": "add_track", "args": {"type": "audio"}}])

        ins = self.client.inspect(clips=False)
        tracks = ins.get("tracks", [])
        audio_track_idx = None
        video_track_idx = None
        for t in tracks:
            if t.get("type") == "audio" and audio_track_idx is None:
                audio_track_idx = t.get("i", 0)
            elif t.get("type") == "video" and video_track_idx is None:
                video_track_idx = t.get("i", 0)

        if audio_track_idx is None:
            audio_track_idx = 0
        if video_track_idx is None:
            video_track_idx = 0

        # Step 4: Place clips (omitting explicit track so Drift natively directs to the right audio/video lane)
        placed_ops: List[Dict[str, Any]] = []
        for scene in plan.scenes:
            # Place narration audio
            if scene.audio_path and os.path.exists(scene.audio_path):
                audio_name = Path(scene.audio_path).name
                asset_id = imported_assets.get(audio_name) or imported_assets.get(str(Path(scene.audio_path).resolve()))
                if asset_id:
                    placed_ops.append({
                        "tool": "place_clip",
                        "args": {
                            "asset": asset_id,
                            "at": scene.start_time
                        }
                    })

            # Place video clip
            if scene.selected_media and scene.selected_media.local_cached_path:
                loc = scene.selected_media.local_cached_path
                if os.path.exists(loc):
                    vid_name = Path(loc).name
                    asset_id = imported_assets.get(vid_name) or imported_assets.get(str(Path(loc).resolve()))
                    if asset_id:
                        placed_ops.append({
                            "tool": "place_clip",
                            "args": {
                                "asset": asset_id,
                                "at": scene.start_time
                            }
                        })

        # Apply placements
        if placed_ops:
            place_res = self.client.apply(placed_ops)

        # Inspect placed clips to apply volume silencing, Ken Burns and transitions
        ins_after = self.client.inspect(clips=True)
        all_tracks = ins_after.get("tracks", [])
        video_track_idx = None
        audio_track_idx = None
        for t in all_tracks:
            if t.get("type") == "video" and video_track_idx is None:
                video_track_idx = t.get("i", 0)
            elif t.get("type") == "audio" and audio_track_idx is None:
                audio_track_idx = t.get("i", 1)

        video_clip_count = 0
        for tr in all_tracks:
            if tr.get("type") == "video":
                for item in tr.get("items", []):
                    clip_uuid = item.get("id") or item.get("clip")
                    if clip_uuid:
                        video_clip_count += 1
                        # 1. Silence native audio of stock footage
                        try:
                            self.client.apply([{
                                "tool": "set_volume",
                                "args": {"clip": clip_uuid, "volume": 0.0}
                            }])
                        except Exception:
                            pass

                        # 2. Ken Burns Motion for static images
                        if plan.config.enable_ken_burns:
                            item_start = item.get("start", 0.0)
                            matched_scene = next((s for s in plan.scenes if abs(s.start_time - item_start) < 0.5), None)
                            if matched_scene and matched_scene.selected_media:
                                is_img = (
                                    matched_scene.selected_media.media_type == "image" or
                                    (matched_scene.selected_media.local_cached_path and 
                                     matched_scene.selected_media.local_cached_path.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
                                )
                                if is_img:
                                    try:
                                        self.client.apply([{
                                            "tool": "set_animation",
                                            "args": {
                                                "clip": clip_uuid,
                                                "which": "animIn",
                                                "kind": "zoomIn",
                                                "duration": max(2.0, matched_scene.duration)
                                            }
                                        }])
                                    except Exception:
                                        pass

        # Step 5: Cinematographic Transitions between scenes
        if plan.config.transition_kind and plan.config.transition_kind != "none" and video_clip_count > 1:
            for c_idx in range(video_clip_count - 1):
                try:
                    self.client.apply([{
                        "tool": "add_transition",
                        "args": {
                            "track": video_track_idx,
                            "index": c_idx,
                            "kind": plan.config.transition_kind,
                            "duration": 0.5
                        }
                    }])
                except Exception:
                    pass

        # Step 6: Background Music with Auto-Ducking
        if plan.config.background_music and plan.config.background_music_path and os.path.exists(plan.config.background_music_path):
            music_abs = str(Path(plan.config.background_music_path).resolve())
            imp_music = self.client.apply([{"tool": "import_media", "args": {"paths": [music_abs]}}])
            done_m = imp_music.get("done", [])
            if done_m and "result" in done_m[0]:
                m_assets = done_m[0]["result"].get("assets", [])
                if m_assets:
                    m_id = m_assets[0].get("id")
                    self.client.apply([{"tool": "add_track", "args": {"type": "audio"}}])
                    ins_post = self.client.inspect(clips=False)
                    all_tracks = ins_post.get("tracks", [])
                    music_track_idx = all_tracks[-1].get("i", 2) if all_tracks else 2
                    self.client.apply([{
                        "tool": "place_clip",
                        "args": {"asset": m_id, "at": 0.0, "track": music_track_idx}
                    }])
                    # Apply Auto-Ducking under narration track
                    if plan.config.auto_ducking and audio_track_idx is not None:
                        self.client.apply([{
                            "tool": "duck_under",
                            "args": {
                                "track": music_track_idx,
                                "index": 0,
                                "over_track": audio_track_idx,
                                "amount": 0.25
                            }
                        }])

        # Step 7: Subtitles (if enabled)
        if plan.config.enable_subtitles:
            cues = CaptionManager.build_subtitle_cues(plan.scenes)
            if cues:
                sub_res = self.client.apply([{
                    "tool": "add_subtitle_clip",
                    "args": {"at": 0.0}
                }])
                done_sub = sub_res.get("done", [])
                if done_sub and "result" in done_sub[0]:
                    sub_clip = done_sub[0]["result"].get("clip")
                    if sub_clip:
                        self.client.apply([{
                            "tool": "set_subtitle_cues",
                            "args": {"clip": sub_clip, "cues": cues}
                        }])

        for s in plan.scenes:
            s.state = SceneState.PLACED

        # Step 8: Save native .drift project bundle
        safe_title = "".join(c for c in plan.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        drift_proj_path = str((Path("d:/CUTWIREDRIFT") / f"{safe_title or 'projeto_drift'}.drift").resolve())
        try:
            self.client.apply([{
                "tool": "save_project",
                "args": {"path": drift_proj_path}
            }])
        except Exception:
            pass

        return {
            "ok": True,
            "project_id": plan.project_id,
            "scenes_placed": len(plan.scenes),
            "total_duration": plan.total_duration(),
            "drift_project_path": drift_proj_path
        }

