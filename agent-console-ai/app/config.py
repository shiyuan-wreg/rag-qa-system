from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ai_demos_base_url: str = "http://localhost:8001"
    internal_key: str = "changeme"
    max_timeout: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
