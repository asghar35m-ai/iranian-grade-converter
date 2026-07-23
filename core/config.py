from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://papergene:change-me@localhost:5432/papergene"
    redis_url: str = "redis://localhost:6379/0"
    http_cache_path: str = ".cache/http_cache.sqlite"
    ncbi_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    """requests.Session, die jede Antwort cacht und dabei die Rate begrenzt."""


def get_session(host: str, max_calls: int, period: float) -> CachedLimiterSession:
    """Gecachte, ratenbegrenzte Session fuer einen externen Host.

    Jeder Ingest-Client (Europe PMC, spaeter PubMed, bioRxiv, ...) holt sich
    seine Session hierueber, statt eigenes Caching/Rate-Limiting zu bauen.
    """
    cache_path = Path(get_settings().http_cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    return CachedLimiterSession(
        cache_name=str(cache_path),
        backend=SQLiteCache(str(cache_path)),
        per_host_limiter=True,
        per_second=max_calls / period,
    )
