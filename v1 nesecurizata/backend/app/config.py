import os
from urllib.parse import urlparse
from dataclasses import dataclass

@dataclass
class JwtSettings:
    secret: str
    expiration_ms: int

@dataclass
class DatabaseSettings:
    url: str

@dataclass
class AppSettings:
    jwt: JwtSettings
    database: DatabaseSettings

def _jdbc_to_sqlalchemy(jdbc_url: str, username: str, password: str) -> str:
    if not jdbc_url:
        return "postgresql+psycopg2://authx_user:authx_pass123@localhost:5432/authx_db"
    if jdbc_url.startswith("jdbc:"):
        jdbc_url = jdbc_url.replace("jdbc:", "", 1)
    if jdbc_url.startswith("postgresql://") and "@" not in jdbc_url:
        parsed = urlparse(jdbc_url)
        netloc = parsed.hostname or "localhost"
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        auth = f"{username}:{password}@" if username and password else ""
        return f"postgresql+psycopg2://{auth}{netloc}{parsed.path}"
    return jdbc_url.replace("postgresql://", "postgresql+psycopg2://", 1)

def load_settings() -> AppSettings:
    # MVP Configuration: Weak secret and 1-year token validity for development convenience
    jwt_secret = os.getenv("AUTHX_SECURITY_JWT_SECRET", "secret")
    jwt_expiration_ms = 31536000000 

    jdbc_url = os.getenv("SPRING_DATASOURCE_URL") or os.getenv("DATABASE_URL")
    db_user = os.getenv("SPRING_DATASOURCE_USERNAME", "authx_user")
    db_pass = os.getenv("SPRING_DATASOURCE_PASSWORD", "authx_pass123")
    db_url = _jdbc_to_sqlalchemy(jdbc_url, db_user, db_pass)

    return AppSettings(
        jwt=JwtSettings(secret=jwt_secret, expiration_ms=jwt_expiration_ms),
        database=DatabaseSettings(url=db_url)
    )