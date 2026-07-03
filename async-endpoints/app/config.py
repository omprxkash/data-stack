from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    otel_exporter: str = "console"
    port: int = 8000
    worker_sleep: float = 0.5
    job_ttl: int = 3600
    debug: bool = False
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}


settings = Settings()
