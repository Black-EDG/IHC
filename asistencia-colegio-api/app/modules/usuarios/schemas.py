from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re
from app.modules.usuarios.models import RolUsuario, EstadoUsuario

class UsuarioBase(BaseModel):
    dni: str = Field(..., min_length=8, max_length=8, pattern=r'^\d{8}$', description="DNI de 8 dígitos")
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    celular: Optional[str] = Field(None, min_length=9, max_length=9, pattern=r'^\d{9}$', description="Celular 9 dígitos")
    correo: EmailStr
    rol: RolUsuario
    estado: Optional[EstadoUsuario] = EstadoUsuario.activo

    @field_validator('nombres', 'apellidos')
    @classmethod
    def capitalizar_nombres(cls, v: str) -> str:
        """Asegura que los nombres y apellidos estén correctamente capitalizados"""
        return ' '.join(word.capitalize() for word in v.strip().split())

    class Config:
        from_attributes = True

class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="Contraseña (mín 8 caracteres, debe incluir mayúscula, minúscula y número)"
    )

    @field_validator('contrasena')
    @classmethod
    def validar_fortaleza_contrasena(cls, v: str) -> str:
        """Valida que la contraseña cumpla con políticas de seguridad"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    celular: Optional[str] = Field(None, min_length=9, max_length=9, pattern=r'^\d{9}$')
    correo: Optional[EmailStr] = None
    rol: Optional[RolUsuario] = None
    estado: Optional[EstadoUsuario] = None
    contrasena: Optional[str] = Field(None, min_length=8, max_length=128)

    @field_validator('contrasena')
    @classmethod
    def validar_contrasena_opcional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.search(r'[A-Z]', v):
                raise ValueError('La contraseña debe contener al menos una mayúscula')
            if not re.search(r'[a-z]', v):
                raise ValueError('La contraseña debe contener al menos una minúscula')
            if not re.search(r'\d', v):
                raise ValueError('La contraseña debe contener al menos un número')
        return v

    class Config:
        from_attributes = True

class UsuarioResponse(BaseModel):
    id: int
    dni: str
    nombres: str
    apellidos: str
    nombre_completo: str
    celular: Optional[str]
    correo: EmailStr
    rol: RolUsuario
    estado: EstadoUsuario
    creado_en: datetime

    class Config:
        from_attributes = True

class UsuarioLoginResponse(BaseModel):
    """Respuesta reducida después del login (sin datos sensibles innecesarios)"""
    id: int
    dni: str
    nombre_completo: str
    rol: RolUsuario
    estado: EstadoUsuario

    class Config:
        from_attributes = True