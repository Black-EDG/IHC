from typing import Optional
from passlib.context import CryptContext

# Configuración del contexto de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obtener_contrasena_hash(contrasena: str) -> str:
    """Recibe la contraseña limpia del frontend y la devuelve encriptada en un hash ilegible"""
    return pwd_context.hash(contrasena)

def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    """Compara la contraseña del login contra el hash guardado en la BD"""
    return pwd_context.verify(contrasena_plana, contrasena_hash)

import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

def crear_token_acceso(data: dict, tiempo_expiracion: Optional[timedelta] = None) -> str:
    """Genera un token JWT firmado y seguro con tiempo de expiración"""
    a_encriptar = data.copy()
    
    # Configurar el tiempo de vida del token
    if tiempo_expiracion:
        expiracion = datetime.now(timezone.utc) + tiempo_expiracion
    else:
        expiracion = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    # Añadir la fecha de expiración al cuerpo (payload) del token
    a_encriptar.update({"exp": expiracion})
    
    # Firmar el token usando nuestra SECRET_KEY del archivo .env
    token_firmado = jwt.encode(a_encriptar, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token_firmado