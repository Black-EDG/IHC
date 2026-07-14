import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from app.core.config import settings

# ═══════════════════════════════════════════════════════════════
# HASHING DE CONTRASEÑAS
# ═══════════════════════════════════════════════════════════════

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obtener_contrasena_hash(contrasena: str) -> str:
    """Encripta una contraseña en texto plano usando bcrypt"""
    return pwd_context.hash(contrasena)

def verificar_contrasena(contrasena_plana: str, hash_almacenado: str) -> bool:
    """Verifica si una contraseña coincide con su hash"""
    return pwd_context.verify(contrasena_plana, hash_almacenado)

# ═══════════════════════════════════════════════════════════════
# JWT TOKENS
# ═══════════════════════════════════════════════════════════════

SECRET_KEY = settings.SECRET_KEY      # ← CAMBIADO
ALGORITHM = settings.ALGORITHM         # ← CAMBIADO
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS  # ← CORREGIDO

def crear_token_acceso(
    data: Dict[str, Any],
    tipo_usuario: str = "personal",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Crea un JWT token de acceso."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
        "tipo_usuario": tipo_usuario,
        "tipo_token": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def crear_token_refresh(
    data: Dict[str, Any],
    tipo_usuario: str = "personal"
) -> str:
    """Crea un JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
        "tipo_usuario": tipo_usuario,
        "tipo_token": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decodificar_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica y valida un JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def extraer_jti(token: str) -> Optional[str]:
    """Extrae el JTI (ID único) de un token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload.get("jti")
    except jwt.InvalidTokenError:
        return None

# ═══════════════════════════════════════════════════════════════
# SMS (SIMULACIÓN PARA DESARROLLO)
# ═══════════════════════════════════════════════════════════════

def generar_codigo_sms() -> str:
    """Genera un código de 4 dígitos para verificación SMS"""
    return ''.join(secrets.choice('0123456789') for _ in range(4))

def verificar_codigo_sms(codigo_ingresado: str, codigo_esperado: str = "1234") -> bool:
    """Verifica el código SMS ingresado."""
    return codigo_ingresado == codigo_esperado

def enmascarar_celular(celular: str) -> str:
    """Enmascara un número de celular: 987654321 → 987***321"""
    if len(celular) >= 9:
        return celular[:3] + "***" + celular[-3:]
    return celular