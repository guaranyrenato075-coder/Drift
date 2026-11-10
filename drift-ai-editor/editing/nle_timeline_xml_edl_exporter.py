"""
Módulo de Exportação de Timelines NLE (Non-Linear Editing).
Permite exportar o projeto gerado pela IA para softwares profissionais de edição:
- Final Cut Pro XML (Premiere Pro, DaVinci Resolve, Final Cut 7)
- DaVinci Resolve EDL (Edit Decision List CMX 3600)
- FCPXML moderno (Final Cut Pro X / DaVinci Resolve)
"""

import os
from typing import Dict, Any, List, Optional
from xml.sax.saxutils import escape


class NLETimelineXMLEdlExporter:
    """
    Exportador de linhas do tempo para suítes de edição NLE de cinema (DaVinci, Premiere, FCP).
    """

    @staticmethod
    def _frames_to_timecode(frames: int, fps: float = 30.0) -> str:
        """Converte número de quadros em formato SMPTE HH:MM:SS:FF."""
        total_seconds = int(frames / fps)
        ff = int(frames % fps)
        ss = int(total_seconds % 60)
        mm = int((total_seconds // 60) % 60)
        hh = int(total_seconds // 3600)
        return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

    @staticmethod
    def export_edl_cmx3600(scenes: List[Dict[str, Any]], fps: float = 30.0, reel_name: str = "DRIFT") -> str:
        """
        Gera uma Edit Decision List (EDL) no formato CMX 3600 padrão da indústria.
        """
        lines = [
            f"TITLE: DRIFT_PROJECT_TIMELINE",
            f"FCM: NON-DROP FRAME",
            ""
        ]

        current_record_frame = 0

        for idx, sc in enumerate(scenes, 1):
            duration = float(sc.get("duration", 4.0))
            scene_frames = int(duration * fps)
            src_in_frame = 0
            src_out_frame = scene_frames
            rec_in_frame = current_record_frame
            rec_out_frame = current_record_frame + scene_frames

            src_in = NLETimelineXMLEdlExporter._frames_to_timecode(src_in_frame, fps)
            src_out = NLETimelineXMLEdlExporter._frames_to_timecode(src_out_frame, fps)
            rec_in = NLETimelineXMLEdlExporter._frames_to_timecode(rec_in_frame, fps)
            rec_out = NLETimelineXMLEdlExporter._frames_to_timecode(rec_out_frame, fps)

            # CMX 3600 line format: EventNum Reel Track Trans SourceIn SourceOut RecordIn RecordOut
            lines.append(f"{idx:03d}  {reel_name[:8]:<8} V     C        {src_in} {src_out} {rec_in} {rec_out}")
            clip_name = sc.get("clip_name") or f"Scene_{idx:02d}.mp4"
            lines.append(f"* FROM CLIP NAME: {clip_name}")
            concept = sc.get("concept", "")
            if concept:
                lines.append(f"* COMMENT: {concept}")
            lines.append("")

            current_record_frame = rec_out_frame

        return "\n".join(lines)

    @staticmethod
    def export_fcp_xml(
        project_name: str,
        scenes: List[Dict[str, Any]],
        fps: float = 30.0,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Gera XML no formato Apple Final Cut Pro 7 / Adobe Premiere Pro XML.
        """
        total_duration_sec = sum(float(sc.get("duration", 4.0)) for sc in scenes)
        total_duration_frames = int(total_duration_sec * fps)
        timebase = int(round(fps))

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!DOCTYPE xmeml>',
            '<xmeml version="4">',
            '  <project>',
            f'    <name>{escape(project_name)}</name>',
            '    <children>',
            '      <sequence>',
            f'        <name>{escape(project_name)}_Sequence</name>',
            f'        <duration>{total_duration_frames}</duration>',
            '        <rate>',
            f'          <timebase>{timebase}</timebase>',
            f'          <ntsc>{"TRUE" if abs(fps - 29.97) < 0.05 else "FALSE"}</ntsc>',
            '        </rate>',
            '        <media>',
            '          <video>',
            '            <format>',
            '              <samplecharacteristics>',
            f'                <width>{width}</width>',
            f'                <height>{height}</height>',
            '                <rate>',
            f'                  <timebase>{timebase}</timebase>',
            '                </rate>',
            '              </samplecharacteristics>',
            '            </format>',
            '            <track>'
        ]

        current_frame = 0
        for idx, sc in enumerate(scenes, 1):
            dur = float(sc.get("duration", 4.0))
            clip_frames = int(dur * fps)
            start_f = current_frame
            end_f = current_frame + clip_frames
            clip_name = sc.get("clip_name") or f"Scene_{idx:02d}.mp4"
            clip_path = sc.get("file_path") or f"file://localhost/{clip_name}"

            xml_lines.extend([
                '              <clipitem id="clipitem-' + str(idx) + '">',
                f'                <name>{escape(clip_name)}</name>',
                f'                <duration>{clip_frames}</duration>',
                '                <rate>',
                f'                  <timebase>{timebase}</timebase>',
                '                </rate>',
                f'                <start>{start_f}</start>',
                f'                <end>{end_f}</end>',
                f'                <in>0</in>',
                f'                <out>{clip_frames}</out>',
                '                <file id="file-' + str(idx) + '">',
                f'                  <name>{escape(clip_name)}</name>',
                f'                  <pathurl>{escape(clip_path)}</pathurl>',
                '                  <rate>',
                f'                    <timebase>{timebase}</timebase>',
                '                  </rate>',
                f'                  <duration>{clip_frames}</duration>',
                '                </file>',
                '              </clipitem>'
            ])
            current_frame = end_f

        xml_lines.extend([
            '            </track>',
            '          </video>',
            '        </media>',
            '      </sequence>',
            '    </children>',
            '  </project>',
            '</xmeml>'
        ])

        return "\n".join(xml_lines)

    @classmethod
    def export_all_formats(
        cls,
        project_name: str,
        scenes: List[Dict[str, Any]],
        output_dir: str,
        fps: float = 30.0
    ) -> Dict[str, Any]:
        """
        Exporta todos os formatos NLE (EDL e Premiere/DaVinci XML) para a pasta informada.
        """
        os.makedirs(output_dir, exist_ok=True)

        edl_content = cls.export_edl_cmx3600(scenes, fps=fps)
        edl_filename = f"{project_name}_timeline.edl"
        edl_path = os.path.join(output_dir, edl_filename)
        with open(edl_path, "w", encoding="utf-8") as f:
            f.write(edl_content)

        xml_content = cls.export_fcp_xml(project_name, scenes, fps=fps)
        xml_filename = f"{project_name}_timeline.xml"
        xml_path = os.path.join(output_dir, xml_filename)
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        total_dur = sum(float(s.get("duration", 4.0)) for s in scenes)

        return {
            "status": "success",
            "project_name": project_name,
            "scene_count": len(scenes),
            "total_duration_sec": round(total_dur, 2),
            "fps": fps,
            "files": {
                "cmx3600_edl": edl_path,
                "premiere_davinci_xml": xml_path
            },
            "summary": f"Linhas do tempo exportadas com sucesso: EDL ({len(scenes)} cortes) e XML para Premiere/DaVinci Resolve."
        }
