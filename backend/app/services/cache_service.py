import time
import hashlib
import json
import asyncio
from collections import OrderedDict
from typing import Any, Optional, Tuple, Dict

class AsyncTTLCache:
    """
    High-performance, in-memory Least-Recently-Used (LRU) cache with Time-To-Live (TTL).
    Thread-safe and async-safe via asyncio.Lock.
    Zero external dependencies ($0 cost, pure Python).
    """
    def __init__(self, maxsize: int = 2000, default_ttl_seconds: int = 86400):
        self.maxsize = maxsize
        self.default_ttl = default_ttl_seconds
        self._cache: OrderedDict[str, Tuple[float, Any]] = OrderedDict()
        self._lock = asyncio.Lock()
        
        # Performance metrics
        self.hits = 0
        self.misses = 0

    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """
        Generates a deterministic SHA-256 cache key from function parameters.
        """
        raw_repr = json.dumps({"prefix": prefix, "args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return f"{prefix}:{hashlib.sha256(raw_repr.encode('utf-8')).hexdigest()}"

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None

            expire_at, value = self._cache[key]
            if time.time() > expire_at:
                # Expired
                del self._cache[key]
                self.misses += 1
                return None

            # Mark as recently used (move to end)
            self._cache.move_to_end(key)
            self.hits += 1
            return value

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expire_at = time.time() + ttl

        async with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (expire_at, value)

            # Evict oldest entry if capacity exceeded
            if len(self._cache) > self.maxsize:
                self._cache.popitem(last=False)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0

    async def get_stats(self) -> Dict[str, Any]:
        async with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0.0
            
            # Count currently unexpired entries
            now = time.time()
            active_count = sum(1 for exp, _ in self._cache.values() if exp > now)

            return {
                "active_cached_items": active_count,
                "max_capacity": self.maxsize,
                "hits": self.hits,
                "misses": self.misses,
                "total_queries": total,
                "hit_rate_percentage": round(hit_rate, 2),
                "storage_type": "in-memory (pure Python $0)"
            }


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter to protect the Gemini API free tier (15 RPM limit).
    Limits requests per client identifier (IP address) over a rolling time window.
    Zero external dependencies ($0 cost).
    """
    def __init__(self, max_requests: int = 12, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._records: Dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def check(self, client_id: str) -> Tuple[bool, int]:
        """
        Checks whether client is allowed to proceed.
        Returns (is_allowed, seconds_until_reset).
        """
        now = time.time()
        cutoff = now - self.window_seconds

        async with self._lock:
            timestamps = self._records.get(client_id, [])
            # Filter timestamps within current window
            valid_timestamps = [t for t in timestamps if t > cutoff]

            if len(valid_timestamps) >= self.max_requests:
                # Rate limit exceeded; calculate wait time
                earliest = valid_timestamps[0]
                wait_seconds = max(1, int(self.window_seconds - (now - earliest)))
                self._records[client_id] = valid_timestamps
                return False, wait_seconds

            valid_timestamps.append(now)
            self._records[client_id] = valid_timestamps
            return True, 0

    async def get_client_remaining(self, client_id: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        async with self._lock:
            timestamps = [t for t in self._records.get(client_id, []) if t > cutoff]
            return max(0, self.max_requests - len(timestamps))


# Shared singletons for app-wide performance
ai_cache = AsyncTTLCache(maxsize=2000, default_ttl_seconds=86400) # 24-hour cache
ai_rate_limiter = SlidingWindowRateLimiter(max_requests=12, window_seconds=60) # 12 requests per minute per client
