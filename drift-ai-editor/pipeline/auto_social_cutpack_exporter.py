"""
Auto Social Media Cutpack Exporter.
Gera a matriz completa de entregáveis para redes sociais a partir do master do projeto:
16:9 (YouTube), 9:16 (Shorts/Reels), 1:1 (Instagram Feed), 4:5 (Facebook) e Teaser 15s.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class AutoSocialCutpackExporter:
    """Gerencia a matriz de exportação multiformato em lote com 1 clique."""

    SOCIAL_PACK_TEMPLATES = {
        "youtube_master_16x9": {
            "platform": "YouTube / TV / Desktop",
            "aspect_ratio": "16:9",
            "resolution": "1920x1080",
            "fps": 60,
            "bitrate_target": "12M",
            "description": "Master horizontal com nitidez completa e som broadcast -14 LUFS."
        },
        "vertical_shorts_9x16": {
            "platform": "YouTube Shorts / TikTok / Reels",
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "fps": 60,
            "bitrate_target": "8M",
            "description": "Formato vertical imersivo para smartphones com fundo blur estendido."
        },
        "square_feed_1x1": {
            "platform": "Instagram Feed / LinkedIn / Twitter",
            "aspect_ratio": "1:1",
            "resolution": "1080x1080",
            "fps": 30,
            "bitrate_target": "5M",
            "description": "Quadrado perfeito otimizado para scroll de feed em desktops e tablets."
        },
        "portrait_feed_4x5": {
            "platform": "Instagram Portrait / Facebook Mobile",
            "aspect_ratio": "4:5",
            "resolution": "1080x1350",
            "fps": 30,
            "bitrate_target": "6M",
            "description": "Retrato vertical que ocupa 75% da tela do celular no feed."
        },
        "teaser_trailer_15s": {
            "platform": "Instagram Stories / WhatsApp Status",
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "fps": 30,
            "bitrate_target": "6M",
            "description": "Teaser ultrarrápido de 15 segundos com CTA de clique no link da bio."
        }
    }

    @classmethod
    def get_cutpack_templates(cls) -> Dict[str, Dict[str, Any]]:
        return cls.SOCIAL_PACK_TEMPLATES

    @classmethod
    def generate_cutpack_render_plan(cls, plan: ProjectPlan, output_directory: str = "exports/cutpack") -> Dict[str, Any]:
        """Gera a lista completa de comandos FFmpeg e especificações de exportação."""
        scenes = getattr(plan, "scenes", [])
        total_duration = sum(float(getattr(s, "duration", 5.0)) for s in scenes)
        raw_title = getattr(plan, "title", "video_master").replace(" ", "_").lower()

        cutpack_jobs = []
        for key, templ in cls.SOCIAL_PACK_TEMPLATES.items():
            filename = f"{raw_title}_{key}.mp4"
            target_dur = 15.0 if key == "teaser_trailer_15s" else total_duration

            # Argumentos de escala e crop por aspect ratio
            if templ["aspect_ratio"] == "16:9":
                scale_filter = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
            elif templ["aspect_ratio"] == "9:16":
                scale_filter = "split[v1][v2];[v1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];[v2]scale=1080:-1[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2"
            elif templ["aspect_ratio"] == "1:1":
                scale_filter = "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2"
            elif templ["aspect_ratio"] == "4:5":
                scale_filter = "scale=1080:1350:force_original_aspect_ratio=decrease,pad=1080:1350:(ow-iw)/2:(oh-ih)/2"
            else:
                scale_filter = "scale=1080:1920"

            ffmpeg_cmd = (
                f"ffmpeg -y -i master.mp4 -t {target_dur} -vf \"{scale_filter}\" "
                f"-c:v libx264 -preset fast -b:v {templ['bitrate_target']} "
                f"-c:a aac -b:a 192k \"{output_directory}/{filename}\""
            )

            cutpack_jobs.append({
                "job_id": key,
                "platform": templ["platform"],
                "target_filename": filename,
                "aspect_ratio": templ["aspect_ratio"],
                "resolution": templ["resolution"],
                "duration_seconds": target_dur,
                "ffmpeg_command": ffmpeg_cmd
            })

        return {
            "total_cutpack_deliverables": len(cutpack_jobs),
            "output_directory": output_directory,
            "source_duration_seconds": round(total_duration, 2),
            "jobs": cutpack_jobs,
            "status": "READY_FOR_BATCH_EXPORT"
        }
