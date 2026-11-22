"""Minimal in-memory sliding-window rate limiter.

Good enough for a single-instance portfolio. If you scale to several workers or
instances, swap this for Redis (e.g. Flask-Limiter) so limits are shared.
"""
import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self):
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key, limit, window):
        """Record a hit. Returns (allowed, retry_after_seconds)."""
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= window:
                hits.popleft()
            if len(hits) >= limit:
                return False, int(window - (now - hits[0])) + 1
            hits.append(now)
            if len(self._hits) > 10_000:  # bound memory under abuse
                self._hits = defaultdict(deque, {key: hits})
            return True, 0

    def reset(self):
        with self._lock:
            self._hits.clear()


limiter = RateLimiter()
