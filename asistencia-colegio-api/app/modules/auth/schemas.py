from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# LOGIN PERSONAL (ADMIN, AUXILIAR, DOCENTE)
# ═══════════════════════════════════════════════════════════════

class LoginPersonalRequest(BaseModel):
    """Credenciales de login para personal del colegio - USA CORREO"""
    correo: EmailStr = Field(..., description="Correo institucional del personal")
    contrasena: str = Field(..., min_length=6, description="Contraseña de acceso")
    
    class Config:
        json_schema_extra = {
            "example": {
                "correo": "admin@colegioabancay.edu.pe",
                "contrasena": "MiContraseña123"
            }
        }

class LoginPersonalResponse(BaseModel):
    """Respuesta exitosa de login del personal"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    usuario: dict
    dashboard: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "usuario": {
                    "id": 1,
                    "dni": "12345678",
                    "nombre_completo": "Juan Pérez",
                    "correo": "juan.perez@colegioabancay.edu.pe",
                    "rol": "docente"
                },
                "dashboard": {
                    "asignaciones_docente": [],
                    "asignaciones_tutor": [],
                    "total_asignaciones": 0
                }
            }
        }

# ═══════════════════════════════════════════════════════════════
# LOGIN APODERADO (PADRE DE FAMILIA)
# ═══════════════════════════════════════════════════════════════

class LoginApoderadoRequest(BaseModel):
    """Login simplificado para padres: solo DNI"""
    dni: str = Field(..., min_length=8, max_length=8, pattern=r'^\d{8}$', description="DNI del padre/apoderado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dni": "87654321"
            }
        }

class LoginApoderadoConSMSRequest(BaseModel):
    """Login con verificación SMS (opcional pero recomendado)"""
    dni: str = Field(..., min_length=8, max_length=8, pattern=r'^\d{8}$')
    codigo_sms: str = Field(..., min_length=4, max_length=6, description="Código recibido por SMS")

class LoginApoderadoResponse(BaseModel):
    """Respuesta exitosa de login del apoderado"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    apoderado: dict
    hijos: List[dict] = []
    mensaje: str = "Seleccione a su hijo para continuar"

class HijoBandejaResponse(BaseModel):
    """Hijo en la bandeja de selección"""
    id: int
    nombre_completo: str
    dni: str
    grado_seccion: str
    estado: str

# ═══════════════════════════════════════════════════════════════
# RENOVACIÓN DE TOKEN
# ═══════════════════════════════════════════════════════════════

class RefreshTokenRequest(BaseModel):
    """Solicitud para renovar el access token"""
    refresh_token: str = Field(..., description="Refresh token obtenido en el login")

class RefreshTokenResponse(BaseModel):
    """Nuevo access token"""
    access_token: str
    token_type: str = "bearer"
    expira_en: int  # Segundos hasta expiración

# ═══════════════════════════════════════════════════════════════
# RESPUESTAS GENERALES
# ═══════════════════════════════════════════════════════════════

class LogoutResponse(BaseModel):
    """Respuesta de cierre de sesión"""
    mensaje: str = "Sesión cerrada correctamente. Token revocado."
    status: str = "success"

class VerificarTokenResponse(BaseModel):
    """Respuesta de verificación de token"""
    valido: bool
    tipo_usuario: Optional[str] = None
    user_id: Optional[int] = None
    rol: Optional[str] = None
    expira_en: Optional[datetime] = None