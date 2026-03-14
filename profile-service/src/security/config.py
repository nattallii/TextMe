from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()