from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from models.scene_plan import ProjectPlan, Scene
from pipeline.style_engine import StyleEngine, StyleProfile

@dataclass
class TimelineOperation:
    stage_name: str
    tool: str
    args: Dict[str, Any]
    description: str
    critical: bool = True

@dataclass
class AssemblyPlan:
    project_id: str
    total_duration_sec: float
    total_scenes: int
    batches: List[List[TimelineOperation]] = field(default_factory=list)
    validation_passed: bool = False
    validation_issues: List[str] = field(default_factory=list)

class TimelinePlanner:
    """
    Constructs a verified, conflict-free sequence of timeline operations before
    dispatching calls to Drift's MCP server. Divides operations into recoverable batches
    (e.g., track setup -> audio voiceover -> video clips -> transitions -> music ducking -> captions).
    """

    @classmethod
    def create_assembly_plan(
        cls,
        plan: ProjectPlan,
        style_profile: Optional[StyleProfile] = None
    ) -> AssemblyPlan:
        if style_profile is None:
            style_profile = StyleEngine.get_profile("filosofico")

        ops_batch_tracks: List[TimelineOperation] = []
        ops_batch_voice: List[TimelineOperation] = []
        ops_batch_video: List[TimelineOperation] = []
        ops_batch_transitions: List[TimelineOperation] = []
        ops_batch_captions: List[TimelineOperation] = []

        total_time_us = 0
        issues: List[str] = []

        # 1. Setup Tracks
        ops_batch_tracks.append(
            TimelineOperation(
                stage_name="track_setup",
                tool="clear_timeline",
                args={},
                description="Limpa a timeline anterior para montagem limpa"
            )
        )
        ops_batch_tracks.append(
            TimelineOperation(
                stage_name="track_setup",
                tool="add_track",
                args={"kind": "video", "name": "V1 - Video & Imagens"},
                description="Cria faixa de vídeo principal"
            )
        )
        ops_batch_tracks.append(
            TimelineOperation(
                stage_name="track_setup",
                tool="add_track",
                args={"kind": "audio", "name": "A1 - Narração IA"},
                description="Cria faixa de voz principal"
            )
        )

        # 2. Iterate through scenes and calculate exact timings
        cur_pos_us = 0
        for idx, scene in enumerate(plan.scenes):
            scene_dur_us = int((scene.duration or 4.0) * 1_000_000)

            # Check for audio file
            audio_p = getattr(scene, "audio_path", None) or getattr(scene, "narration_audio_path", None)
            if audio_p:
                audio_file = Path(audio_p)
                if not audio_file.exists():
                    issues.append(f"Cena {scene.order}: Arquivo de áudio não encontrado ({audio_file.name})")
                else:
                    ops_batch_voice.append(
                        TimelineOperation(
                            stage_name="voice_placement",
                            tool="insert_clip",
                            args={
                                "track_index": 1,
                                "path": str(audio_file.resolve()),
                                "in_point_us": 0,
                                "out_point_us": scene_dur_us,
                                "timeline_in_us": cur_pos_us
                            },
                            description=f"Insere narração da Cena {scene.order}"
                        )
                    )

            # Check for media clip
            if scene.selected_media and scene.selected_media.local_cached_path:
                media_path = Path(scene.selected_media.local_cached_path)
                if not media_path.exists():
                    issues.append(f"Cena {scene.order}: Mídia visual não baixada ({scene.selected_media.title})")
                else:
                    ops_batch_video.append(
                        TimelineOperation(
                            stage_name="media_placement",
                            tool="insert_clip",
                            args={
                                "track_index": 0,
                                "path": str(media_path.resolve()),
                                "in_point_us": 0,
                                "out_point_us": scene_dur_us,
                                "timeline_in_us": cur_pos_us,
                                "track_audio_mode": "muted"
                            },
                            description=f"Insere vídeo/imagem da Cena {scene.order}"
                        )
                    )

                    # If static image, schedule Ken Burns animation
                    is_image = media_path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
                    if is_image:
                        zoom_target = style_profile.ken_burns_intensity
                        ops_batch_video.append(
                            TimelineOperation(
                                stage_name="ken_burns",
                                tool="set_animation",
                                args={
                                    "track_index": 0,
                                    "clip_index": idx,
                                    "animation": "ken_burns_zoom_in",
                                    "start_scale": 1.0,
                                    "end_scale": zoom_target
                                },
                                description=f"Aplica efeito Ken Burns dinâmico na Cena {scene.order}",
                                critical=False
                            )
                        )

                    # Crossfade transition (between scenes)
                    if idx > 0 and style_profile.transition_duration_ms > 0:
                        ops_batch_transitions.append(
                            TimelineOperation(
                                stage_name="transition",
                                tool="add_transition",
                                args={
                                    "track_index": 0,
                                    "left_clip_index": idx - 1,
                                    "right_clip_index": idx,
                                    "kind": style_profile.transition_type,
                                    "duration_ms": style_profile.transition_duration_ms
                                },
                                description=f"Adiciona transição {style_profile.transition_type} entre cena {idx} e {idx+1}",
                                critical=False
                            )
                        )

            cur_pos_us += scene_dur_us

        total_time_us = cur_pos_us
        total_sec = total_time_us / 1_000_000

        batches = [
            ops_batch_tracks,
            ops_batch_voice,
            ops_batch_video,
            ops_batch_transitions
        ]

        return AssemblyPlan(
            project_id=plan.project_id,
            total_duration_sec=round(total_sec, 2),
            total_scenes=len(plan.scenes),
            batches=[b for b in batches if b],
            validation_passed=len(issues) == 0,
            validation_issues=issues
        )
