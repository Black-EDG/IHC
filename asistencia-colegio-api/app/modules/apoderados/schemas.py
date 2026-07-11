from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class ApoderadoBase(BaseModel):
    dni: str = Field(..., min_length=8, max_length=8, description="DNI del titular")
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    celular: str = Field(..., min_length=9, max_length=9, description="Celular del titular (9 dígitos)")
    parentesco: str = Field(..., min_length=3, max_length=30)
    correo: Optional[EmailStr] = None

    # Datos opcionales de respaldo
    contacto_emergencia_nombre: Optional[str] = Field(None, max_length=150)
    contacto_emergencia_celular: Optional[str] = Field(None, min_length=9, max_length=9)
    contacto_emergencia_parentesco: Optional[str] = Field(None, max_length=30)

    class Config:
        from_attributes = True

class ApoderadoCreate(ApoderadoBase):
    pass

class ApoderadoResponse(ApoderadoBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True