"""
Multilingual Multi-Audio Track Packager for CutWire Drift AI (MrBeast-Style Global Distribution).
Packages video with multiple synced audio tracks (Portuguese, English, Spanish, etc.)
into a single MP4 container recognized by YouTube's Multi-Language Audio feature.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
from models.scene_plan import ProjectPlan

@dataclass
class AudioTrackDefinition:
    language_code: str         # 'por', 'eng', 'spa', 'deu', 'fra', 'jpn'
    title: str                 # 'Português (Original)', 'English (Dubbed)', 'Español'
    audio_file_path: str
    is_default: bool = False
    volume_db: float = 0.0

@dataclass
class MultiAudioExportSpec:
    project_id: str
    video_source_path: str
    output_target_path: str
    tracks: List[AudioTrackDefinition]
    ffmpeg_command_args: List[str]
    supported_platforms: List[str]

class MultilingualAudioPackager:
    """
    Builds MP4 container multiplexing specs with ISO 639-2 language tags for multi-language audio.
    """

    LANGUAGE_MAP = {
        "pt": ("por", "Português"),
        "en": ("eng", "English"),
        "es": ("spa", "Español"),
        "it": ("ita", "Italiano"),
        "de": ("deu", "Deutsch"),
        "fr": ("fra", "Français"),
        "ja": ("jpn", "Japanese"),
        "zh": ("zho", "Mandarin"),
        "ru": ("rus", "Russian")
    }

    @classmethod
    def create_multilingual_spec(
        cls,
        project_id: str,
        video_path: str,
        audio_tracks: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> MultiAudioExportSpec:
        if not output_path:
            base_dir = os.path.dirname(video_path) or "d:/CUTWIREDRIFT"
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(base_dir, f"{base_name}_Global_MultiLang.mp4").replace("\\", "/")

        definitions: List[AudioTrackDefinition] = []
        for idx, tr in enumerate(audio_tracks):
            raw_lang = tr.get("language", "pt").lower()
            iso_code, default_title = cls.LANGUAGE_MAP.get(raw_lang, (raw_lang[:3], raw_lang.title()))
            
            definitions.append(AudioTrackDefinition(
                language_code=iso_code,
                title=tr.get("title", default_title),
                audio_file_path=tr.get("file_path", "").replace("\\", "/"),
                is_default=(idx == 0 or tr.get("is_default", False)),
                volume_db=float(tr.get("volume_db", 0.0))
            ))

        # Monta os argumentos FFmpeg com mapeamento multiplex de múltiplas faixas
        # Exemplo: -i video.mp4 -i pt.mp3 -i en.mp3 -map 0:v -map 1:a -map 2:a ...
        args = ["-i", video_path]
        for tr in definitions:
            args.extend(["-i", tr.audio_file_path])

        args.extend(["-map", "0:v:0"])
        for idx, tr in enumerate(definitions, start=1):
            args.extend(["-map", f"{idx}:a:0"])

        # Codecs: cópia direta de vídeo (lossless) e codificação AAC de alta fidelidade
        args.extend(["-c:v", "copy", "-c:a", "aac", "-b:a", "192k"])

        # Metadados ISO 639-2 e nomes de exibição de faixas para o YouTube Player
        for idx, tr in enumerate(definitions):
            args.extend([
                f"-metadata:s:a:{idx}", f"language={tr.language_code}",
                f"-metadata:s:a:{idx}", f"title={tr.title}",
                f"-metadata:s:a:{idx}", f"handler_name={tr.title}"
            ])
            if tr.is_default:
                args.extend([f"-disposition:a:{idx}", "default"])
            else:
                args.extend([f"-disposition:a:{idx}", "0"])

        args.extend(["-movflags", "+faststart", output_path])

        return MultiAudioExportSpec(
            project_id=project_id,
            video_source_path=video_path,
            output_target_path=output_path,
            tracks=definitions,
            ffmpeg_command_args=args,
            supported_platforms=["YouTube", "Apple TV", "VLC", "ExoPlayer"]
        )

