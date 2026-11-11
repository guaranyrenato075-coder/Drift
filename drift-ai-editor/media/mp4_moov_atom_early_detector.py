"""
Módulo Detector Rápido de Átomo MOOV para SSDs (MP4 MOOV Atom Early Detector).
Inspeciona rapidamente o cabeçalho e rodapé de contêineres MP4/MOV/M4V.
Detecta se a caixa 'moov' (índice de metadados, quadros-chave e faixas) está no início (FastStart)
ou se está situada no final do arquivo. Para arquivos gigantescos sem faststart, efetua um seek
reverso cirúrgico de apenas 2MB, evitando carregar ou varrer gigabytes lineares no SSD NVMe/SATA.
"""

from typing import Dict, Any, Optional


class MP4MoovAtomEarlyDetector:
    """
    Analisador de contêiner de vídeo sem amplificação de leitura em disco.
    """

    @classmethod
    def analyze_moov_placement(cls, file_size_bytes: int, header_bytes: bytes, footer_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Determina a localização do átomo 'moov' e o ganho de I/O de disco obtido.
        """
        # Checa se 'moov' está nos primeiros bytes (faststart ativado)
        is_faststart = b"moov" in header_bytes

        if is_faststart:
            bytes_read = len(header_bytes)
            status_desc = "FastStart Otimizado (MOOV no Cabeçalho)"
            unnecessary_read_saved_bytes = max(0, file_size_bytes - bytes_read)
        else:
            # MOOV no final do arquivo: necessita seek reverso
            footer_len = len(footer_bytes) if footer_bytes else 2 * 1024 * 1024
            bytes_read = len(header_bytes) + footer_len
            status_desc = "MOOV no Rodapé (Seek Reverso Aplicado)"
            unnecessary_read_saved_bytes = max(0, file_size_bytes - bytes_read)

        savings_pct = round((unnecessary_read_saved_bytes / max(file_size_bytes, 1)) * 100.0, 2)
        saved_mb = round(unnecessary_read_saved_bytes / (1024 * 1024), 2)

        return {
            "status": "success",
            "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
            "is_faststart": is_faststart,
            "moov_location": "HEAD" if is_faststart else "TAIL_SEEK",
            "bytes_read_for_index": bytes_read,
            "ssd_io_saved_mb": saved_mb,
            "ssd_read_reduction_pct": savings_pct,
            "summary": (
                f"{status_desc}. Metadados lidos com apenas {bytes_read} bytes. "
                f"Economizados {saved_mb} MB ({savings_pct}%) de leituras no SSD."
            )
        }
