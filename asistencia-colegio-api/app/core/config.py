import os
from typing import Optional, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración central de la aplicación"""
    
    # Configuración general
    APP_NAME: str = "Sistema de Control Escolar - Abancay"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Base de datos
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/colegio_db"
    
    # JWT - AHORA COINCIDEN CON TU .ENV
    SECRET_KEY: str = "clave-secreta-super-segura-cambiar-en-produccion-2026"  # ← Tu .env tiene SECRET_KEY
    ALGORITHM: str = "HS256"  # ← Tu .env tiene ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # SMS (proveedor - opcional)
    SMS_PROVIDER: str = "twilio"
    SMS_ACCOUNT_SID: Optional[str] = None
    SMS_AUTH_TOKEN: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignora variables extra en .env

settings = Settings()