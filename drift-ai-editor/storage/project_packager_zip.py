"""
One-Click Project Packager & Zip Archiver for CutWire Drift AI.
Bundles the complete production project (.drift timeline file, scene narration audio wavs,
subtitles, YouTube chapter timestamps, and copyright license manifests) into a standalone .zip archive.
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from pathlib import Path
import zipfile
import json
import os
from models.scene_plan import ProjectPlan
from pipeline.auto_chaptering import AutoChapteringEngine
from media.copyright_analyzer import CopyrightAnalyzer

@dataclass
class PackageArchiveResult:
    project_id: str
    zip_path: str
    file_count: int
    uncompressed_bytes: int
    compressed_bytes: int
    included_files: List[str]

class ProjectPackagerZip:
    """
    Creates complete, portable zip bundles for project archiving and team transfer.
    """

    @classmethod
    def package_project(cls, plan: ProjectPlan, output_zip_path: Optional[str] = None) -> PackageArchiveResult:
        safe_title = "".join(c for c in plan.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        if not safe_title:
            safe_title = f"projeto_{plan.project_id[:8]}"

        if not output_zip_path:
            output_dir = Path("d:/CUTWIREDRIFT")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_zip = output_dir / f"Pacote_{safe_title}.zip"
        else:
            output_zip = Path(output_zip_path)
            output_zip.parent.mkdir(parents=True, exist_ok=True)

        included_files: List[str] = []
        uncompressed_bytes = 0

        with zipfile.ZipFile(str(output_zip), "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. Project plan JSON manifest
            plan_json = json.dumps(plan.to_dict(), indent=2, ensure_ascii=False)
            zf.writestr(f"{safe_title}/manifesto_projeto.json", plan_json)
            uncompressed_bytes += len(plan_json.encode("utf-8"))
            included_files.append("manifesto_projeto.json")

            # 2. Raw and formatted script
            script_content = f"TÍTULO: {plan.title}\n\n"
            for s in plan.scenes:
                script_content += f"[CENA {s.order}] ({s.duration:.1f}s)\n{s.narration_text}\nVisual: {s.visual_description}\n\n"
            zf.writestr(f"{safe_title}/roteiro_completo.txt", script_content)
            uncompressed_bytes += len(script_content.encode("utf-8"))
            included_files.append("roteiro_completo.txt")

            # 3. YouTube Chapters and timestamps
            yt_chapters = AutoChapteringEngine.generate_youtube_description_block(plan)
            zf.writestr(f"{safe_title}/capitulos_youtube.txt", yt_chapters)
            uncompressed_bytes += len(yt_chapters.encode("utf-8"))
            included_files.append("capitulos_youtube.txt")

            # 4. Copyright and License Audit manifest
            audit = CopyrightAnalyzer.audit_timeline_copyright(plan)
            audit_json = json.dumps(audit.__dict__, indent=2, ensure_ascii=False)
            zf.writestr(f"{safe_title}/licencas_copyright.json", audit_json)
            uncompressed_bytes += len(audit_json.encode("utf-8"))
            included_files.append("licencas_copyright.json")

            # 5. Scene audio files
            for s in plan.scenes:
                if s.audio_path and os.path.exists(s.audio_path):
                    audio_p = Path(s.audio_path)
                    arc_name = f"{safe_title}/audios/cena_{s.order}_{audio_p.name}"
                    zf.write(str(audio_p), arcname=arc_name)
                    sz = audio_p.stat().st_size
                    uncompressed_bytes += sz
                    included_files.append(f"audios/cena_{s.order}_{audio_p.name}")

            # 6. Native Drift project timeline file (if exists in workspace)
            drift_candidate = Path("d:/CUTWIREDRIFT") / f"{safe_title}.drift"
            if drift_candidate.exists():
                zf.write(str(drift_candidate), arcname=f"{safe_title}/{drift_candidate.name}")
                uncompressed_bytes += drift_candidate.stat().st_size
                included_files.append(drift_candidate.name)

        compressed_bytes = output_zip.stat().st_size if output_zip.exists() else 0

        return PackageArchiveResult(
            project_id=plan.project_id,
            zip_path=str(output_zip),
            file_count=len(included_files),
            uncompressed_bytes=uncompressed_bytes,
            compressed_bytes=compressed_bytes,
            included_files=included_files
        )
