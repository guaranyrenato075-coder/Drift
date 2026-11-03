"""
Smart Cache Engine for CutWire Drift AI.
Provides intelligent caching with TTL (Time-To-Live) for repetitive LLM prompts,
agent searches, and video scene analyses. Seamlessly integrates with Redis when available,
with a fast, thread-safe in-memory LRU+TTL fallback.
"""
import time
import threading
import functools
import json
from collections import OrderedDict
from typing import Any, Optional, Dict, Callable

class SmartCache:
    """
    Thread-safe dual-mode cache (Redis client or high-speed in-memory LRU with TTL).
    """

    def __init__(self, max_entries: int = 1000, default_ttl_sec: int = 300, redis_url: Optional[str] = None):
        self.max_entries = max_entries
        self.default_ttl = default_ttl_sec
        self._lock = threading.Lock()
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict() # key -> (val, expire_time)
        self._redis = None
        self._is_redis_active = False

        if redis_url:
            self._init_redis(redis_url)

    def _init_redis(self, url: str):
        try:
            import redis
            client = redis.from_url(url, decode_responses=True)
            client.ping()
            self._redis = client
            self._is_redis_active = True
        except Exception:
            self._redis = None
            self._is_redis_active = False

    def get(self, key: str) -> Optional[Any]:
        # 1. Try Redis if active
        if self._is_redis_active and self._redis:
            try:
                raw = self._redis.get(key)
                if raw is not None:
                    return json.loads(raw)
            except Exception:
                pass

        # 2. In-Memory fallback
        with self._lock:
            if key not in self._store:
                return None
            val, expire_time = self._store[key]
            if time.time() > expire_time:
                del self._store[key]
                return None
            # Move to end (LRU hit)
            self._store.move_to_end(key)
            return val

    def set(self, key: str, value: Any, ttl_sec: Optional[int] = None) -> None:
        ttl = ttl_sec if ttl_sec is not None else self.default_ttl

        # 1. Store in Redis if active
        if self._is_redis_active and self._redis:
            try:
                self._redis.setex(key, ttl, json.dumps(value))
                return
            except Exception:
                pass

        # 2. In-Memory storage
        expire_time = time.time() + ttl
        with self._lock:
            if key in self._store:
                del self._store[key]
            elif len(self._store) >= self.max_entries:
                # Evict oldest entry (LRU)
                self._store.popitem(last=False)
            self._store[key] = (value, expire_time)

    def delete(self, key: str) -> bool:
        deleted = False
        if self._is_redis_active and self._redis:
            try:
                deleted = bool(self._redis.delete(key))
            except Exception:
                pass
        with self._lock:
            if key in self._store:
                del self._store[key]
                deleted = True
        return deleted

    def clear(self) -> None:
        if self._is_redis_active and self._redis:
            try:
                self._redis.flushdb()
            except Exception:
                pass
        with self._lock:
            self._store.clear()

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            active_count = 0
            now = time.time()
            for _, (_, exp) in self._store.items():
                if exp > now:
                    active_count += 1
            return {
                "active_entries": active_count,
                "max_entries": self.max_entries,
                "backend": "redis" if self._is_redis_active else "in_memory_lru",
                "default_ttl_sec": self.default_ttl
            }

# Global singleton smart cache instance
GLOBAL_CACHE = SmartCache()

def cached(prefix: str, ttl_sec: int = 300):
    """
    Decorator to cache function results by arguments.
    """
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Build cache key
            args_repr = [str(a) for a in args]
            kwargs_repr = [f"{k}={v}" for k, v in sorted(kwargs.items())]
            raw_key = f"{prefix}:{fn.__name__}:{'_'.join(args_repr)}:{'_'.join(kwargs_repr)}"
            hit = GLOBAL_CACHE.get(raw_key)
            if hit is not None:
                return hit
            result = fn(*args, **kwargs)
            GLOBAL_CACHE.set(raw_key, result, ttl_sec=ttl_sec)
            return result
        return wrapper
    return decorator

