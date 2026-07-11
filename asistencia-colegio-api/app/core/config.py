import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

#Esto es para forzar la carga del archivo .env de la raiz
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    class config:
        case_sensitive = True

settings = Settings()