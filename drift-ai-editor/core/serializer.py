"""
MessagePack Serializer for CutWire Drift AI.
Enables high-performance binary serialization between Node.js Fastify Gateway,
Python AI Engine, and Redis/cache layers with up to 80% payload size reduction.
"""
from typing import Any

try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False
    import json

class DriftSerializer:
    """
    Lightweight serializer implementing MessagePack with standard JSON fallback.
    """

    @classmethod
    def serialize(cls, data: Any) -> bytes:
        if HAS_MSGPACK:
            return msgpack.packb(data, use_bin_type=True)
        # Fallback to UTF-8 encoded JSON bytes if msgpack is not installed in python
        return json.dumps(data, ensure_ascii=False).encode("utf-8")

    @classmethod
    def deserialize(cls, buffer: bytes) -> Any:
        if HAS_MSGPACK:
            try:
                return msgpack.unpackb(buffer, raw=False)
            except Exception:
                pass
        return json.loads(buffer.decode("utf-8"))

