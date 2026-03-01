from pydantic_settings import BaseSettings

# Ubicación fija: A Coruña (no se usa otra para las recomendaciones)
A_CORUNA_LAT = 43.37
A_CORUNA_LON = -8.40


class Settings(BaseSettings):
    database_url: str = "postgresql://costa:costa_secret@localhost:5432/costa"
    location_id: str = "a_coruna"

    class Config:
        env_file = ".env"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
