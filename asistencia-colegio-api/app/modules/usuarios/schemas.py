from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.modules.usuarios.models import RolUsuario, EstadoUsuario

# 1. Esquema Base con los datos comunes
class UsuarioBase(BaseModel):
    dni: str = Field(..., min_length=8, max_length=8, description="DNI del usuario (8 dígitos)")
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    celular: Optional[str] = Field(None, min_length=9, max_length=9, description="Celular (9 dígitos)")
    correo: EmailStr # Valida automáticamente que sea un correo real (ej: profesor@colegio.edu.pe)
    rol: RolUsuario
    estado: Optional[EstadoUsuario] = EstadoUsuario.activo

    # Configuración para que Pydantic pueda leer datos que vienen de SQLAlchemy
    class Config:
        from_attributes = True

# 2. Esquema para CREAR un usuario (Pide contraseña limpia)
class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=6, description="Contraseña en texto plano para encriptar")

# 3. Esquema para RESPONDER al Frontend (Seguro, sin contraseñas)
class UsuarioResponse(BaseModel):
    id: int
    dni: str
    nombres: str
    apellidos: str
    celular: Optional[str]
    correo: EmailStr
    rol: RolUsuario
    estado: EstadoUsuario
    creado_en: datetime

    class Config:
        from_attributes = True