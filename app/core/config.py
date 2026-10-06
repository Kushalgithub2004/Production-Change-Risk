from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Production Change Risk Intelligence Engine"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://user:password@localhost/risk_engine"

    class Config:
        env_file = ".env"

settings = Settings()
