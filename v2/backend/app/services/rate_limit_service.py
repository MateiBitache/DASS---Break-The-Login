import time
from dataclasses import dataclass
from app.exceptions import AuthException

@dataclass
class Bucket:
    capacity: int
    tokens: int
    last_refill: float

def _refill(bucket: Bucket, now: float):
    elapsed = now - bucket.last_refill
    if elapsed <= 0: return
    refill_rate = bucket.capacity / 60.0
    new_tokens = int(elapsed * refill_rate)
    if new_tokens > 0:
        bucket.tokens = min(bucket.capacity, bucket.tokens + new_tokens)
        bucket.last_refill = now

class RateLimitService:
    def __init__(self):
        self._buckets = {}
        self._lockout = {}
        self.max_attempts = 5
        self.lockout_time = 900 # 15 minutes in seconds

    def check_rate_limit(self, email: str, ip_address: str):
        key = f"{email}:{ip_address}"
        now = time.time()

        lockout_until = self._lockout.get(key)
        if lockout_until is not None:
            if now < lockout_until:
                remaining = int(lockout_until - now)
                raise AuthException(f"Too many login attempts. Try again in {remaining} seconds.")
            self._lockout.pop(key, None)
            self._buckets.pop(key, None)

        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = Bucket(capacity=self.max_attempts, tokens=self.max_attempts, last_refill=now)
            self._buckets[key] = bucket

        _refill(bucket, now)

        if bucket.tokens <= 0:
            self._lockout[key] = now + self.lockout_time
            raise AuthException(f"Too many login attempts. Account locked for {self.lockout_time} seconds.")

        bucket.tokens -= 1

    def is_rate_limiting_enabled(self) -> bool:
        return True

    def reset_rate_limit(self, email: str, ip_address: str):
        key = f"{email}:{ip_address}"
        self._buckets.pop(key, None)
        self._lockout.pop(key, None)