"""
Módulo de Buffer Circular em RAM para Streaming sem Arquivo .TMP (Raw Stream Circular I/O Buffer).
Substitui a criação de arquivos temporários transitórios em disco (.tmp) durante o download
e streaming de fragmentos de mídias e amostras de voz por um buffer circular volátil pré-alocado em RAM.
Zera as operações de escrita e deleção contínua na memória NAND flash do SSD,
reduzindo a degradação de gravação do disco e acelerando o tempo de resposta em tempo real.
"""

from typing import Dict, Any, Optional


class RawStreamCircularIOBuffer:
    """
    Buffer circular em memória volátil de tamanho estático para I/O em tempo de execução.
    """

    DEFAULT_CAPACITY_BYTES = 8 * 1024 * 1024  # 8 MB de pool volátil em RAM

    def __init__(self, capacity_bytes: int = DEFAULT_CAPACITY_BYTES):
        self.capacity_bytes = max(1024, capacity_bytes)
        self._buffer = bytearray(self.capacity_bytes)
        self._head = 0
        self._tail = 0
        self._size = 0
        self._bytes_streamed_total = 0

    def write_stream_chunk(self, chunk: bytes) -> int:
        """Grava dados no anel de buffer em RAM sem tocar no SSD."""
        chunk_len = len(chunk)
        for b in chunk:
            self._buffer[self._head] = b
            self._head = (self._head + 1) % self.capacity_bytes
            if self._size < self.capacity_bytes:
                self._size += 1
            else:
                self._tail = (self._tail + 1) % self.capacity_bytes
        self._bytes_streamed_total += chunk_len
        return chunk_len

    def read_stream_chunk(self, max_bytes: int) -> bytes:
        """Lê os dados descarregados do anel de buffer."""
        to_read = min(max_bytes, self._size)
        out = bytearray(to_read)
        for i in range(to_read):
            out[i] = self._buffer[self._tail]
            self._tail = (self._tail + 1) % self.capacity_bytes
        self._size -= to_read
        return bytes(out)

    def get_io_savings(self) -> Dict[str, Any]:
        """Calcula a quantidade de escritas temporárias em disco eliminadas."""
        saved_mb = round(self._bytes_streamed_total / (1024 * 1024), 2)
        ram_footprint_mb = round(self.capacity_bytes / (1024 * 1024), 2)

        return {
            "status": "success",
            "ring_buffer_capacity_mb": ram_footprint_mb,
            "total_streamed_bytes": self._bytes_streamed_total,
            "disk_writes_avoided_mb": saved_mb,
            "temporary_files_created": 0,
            "ssd_wear_protection": "100% Livre de Arquivos Efêmeros",
            "summary": (
                f"Buffer Circular de {ram_footprint_mb} MB ativo na RAM. "
                f"{saved_mb} MB de arquivos temporários (.tmp) eliminados do SSD com zero escritas em disco."
            )
        }
