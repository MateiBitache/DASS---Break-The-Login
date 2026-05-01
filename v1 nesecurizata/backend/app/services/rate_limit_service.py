class RateLimitService:
    def __init__(self):
        pass

    def check_rate_limit(self, email: str, ip_address: str):
        # VULNERABILITY: Rate limiting is completely disabled
        pass

    def is_rate_limiting_enabled(self) -> bool:
        return False

    def reset_rate_limit(self, email: str, ip_address: str):
        pass