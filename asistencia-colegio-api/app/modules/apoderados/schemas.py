from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
import re
from app.modules.apoderados.models import Parentesco

class ApoderadoBase(BaseModel):
    """Campos base compartidos"""
    dni: str = Field(..., min_length=8, max_length=8, pattern=r'^\d{8}$')
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    celular: str = Field(..., min_length=9, max_length=9, pattern=r'^\d{9}$')
    parentesco: str = Field(..., min_length=2, max_length=30)
    correo: Optional[EmailStr] = None
    
    @field_validator('nombres', 'apellidos')
    @classmethod
    def capitalizar_nombres(cls, v: str) -> str:
        """Capitaliza correctamente los nombres propios"""
        return ' '.join(word.capitalize() for word in v.strip().split())
    
    @field_validator('parentesco')
    @classmethod
    def validar_parentesco(cls, v: str) -> str:
        """Valida que el parentesco esté en la lista permitida"""
        parentescos_validos = [p.value for p in Parentesco]
        # Capitalizar primera letra de cada palabra
        v_capitalizado = ' '.join(word.capitalize() for word in v.strip().split())
        if v_capitalizado not in parentescos_validos:
            # Permitir "Otro" como comodín pero advertir
            if v_capitalizado not in parentescos_validos:
                raise ValueError(
                    f"Parentesco '{v}' no válido. Opciones: {', '.join(parentescos_validos)}"
                )
        return v_capitalizado

    class Config:
        from_attributes = True

class ApoderadoCreate(ApoderadoBase):
    """Esquema para registrar un nuevo apoderado"""
    contacto_emergencia_nombre: Optional[str] = Field(None, max_length=150)
    contacto_emergencia_celular: Optional[str] = Field(None, min_length=9, max_length=9, pattern=r'^\d{9}$')
    contacto_emergencia_parentesco: Optional[str] = Field(None, max_length=30)
    
    @model_validator(mode='after')
    def validar_coherencia_contacto_emergencia(self):
        """
        Si se proporciona algún campo de emergencia, deben proporcionarse todos
        """
        campos_emergencia = [
            self.contacto_emergencia_nombre,
            self.contacto_emergencia_celular,
            self.contacto_emergencia_parentesco
        ]
        
        if any(campos_emergencia) and not all(campos_emergencia):
            raise ValueError(
                "Si registra un contacto de emergencia, debe proporcionar: "
                "nombre, celular y parentesco del contacto."
            )
        
        return self

class ApoderadoUpdate(BaseModel):
    """Esquema para actualizar datos del apoderado (todos opcionales)"""
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    celular: Optional[str] = Field(None, min_length=9, max_length=9, pattern=r'^\d{9}$')
    parentesco: Optional[str] = Field(None, max_length=30)
    correo: Optional[EmailStr] = None
    contacto_emergencia_nombre: Optional[str] = Field(None, max_length=150)
    contacto_emergencia_celular: Optional[str] = Field(None, min_length=9, max_length=9, pattern=r'^\d{9}$')
    contacto_emergencia_parentesco: Optional[str] = Field(None, max_length=30)
    
    class Config:
        from_attributes = True

class HijoBandejaResponse(BaseModel):
    """Respuesta individual para cada hijo en la bandeja de selección"""
    id: int
    nombre_completo: str
    dni: str
    grado: str
    seccion: str
    grado_seccion: str
    estado: str
    
    class Config:
        from_attributes = True

class ApoderadoResponse(BaseModel):
    """Respuesta completa con datos del apoderado"""
    id: int
    dni: str
    nombres: str
    apellidos: str
    nombre_completo: str
    celular: str
    parentesco: str
    correo: Optional[EmailStr]
    contacto_emergencia_nombre: Optional[str]
    contacto_emergencia_celular: Optional[str]
    contacto_emergencia_parentesco: Optional[str]
    celular_verificado: bool
    cantidad_hijos: int
    tiene_contacto_emergencia: bool
    creado_en: datetime
    
    class Config:
        from_attributes = True

class ApoderadoLoginResponse(BaseModel):
    """Respuesta después del login exitoso con DNI"""
    id: int
    dni: str
    nombre_completo: str
    celular: str
    hijos: List[HijoBandejaResponse] = []
    mensaje: str = "Seleccione a su hijo para ver su información"
    
    class Config:
        from_attributes = True

class VerificarCelularRequest(BaseModel):
    """Solicitud para verificar el número de celular"""
    dni: str = Field(..., min_length=8, max_length=8)
    codigo_sms: str = Field(..., min_length=4, max_length=6, description="Código recibido por SMS")

class ApoderadoBusquedaResponse(BaseModel):
    """Respuesta resumida para búsquedas rápidas"""
    id: int
    dni: str
    nombre_completo: str
    celular: str
    parentesco: str
    cantidad_hijos: int
    
    class Config:
        from_attributes = True