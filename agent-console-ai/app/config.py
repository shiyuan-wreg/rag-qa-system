from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    zhipu_api_key: str
    internal_key: str = "changeme"
    default_model: str = "glm-4-flash"
    max_timeout: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
