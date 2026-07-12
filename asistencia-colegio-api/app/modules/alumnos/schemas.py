from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional
from app.modules.alumnos.models import EstadoAlumno

class AlumnoBase(BaseModel):
    dni: str = Field(..., min_length=8, max_length=8, description="DNI del estudiante")
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    genero: str = Field(..., min_length=1, max_length=1, description="'M' o 'F'")
    fecha_nacimiento: date
    aula_id: int = Field(..., description="ID del salón asignado")
    apoderado_id: int = Field(..., description="ID del apoderado a cargo")
    estado: Optional[EstadoAlumno] = EstadoAlumno.matriculado
    suspendido_desde: Optional[date] = None
    suspendido_hasta: Optional[date] = None

    @field_validator('genero')
    @classmethod
    def validar_genero(cls, v: str) -> str:
        if v.upper() not in ('M', 'F'):
            raise ValueError('El género debe ser M o F')
        return v.upper()

    class Config:
        from_attributes = True

class AlumnoCreate(AlumnoBase):
    pass

class AlumnoUpdate(BaseModel):
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    genero: Optional[str] = Field(None, min_length=1, max_length=1)
    fecha_nacimiento: Optional[date] = None
    aula_id: Optional[int] = None
    apoderado_id: Optional[int] = None
    estado: Optional[EstadoAlumno] = None
    suspendido_desde: Optional[date] = None
    suspendido_hasta: Optional[date] = None

    @field_validator('genero')
    @classmethod
    def validar_genero(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.upper() not in ('M', 'F'):
            raise ValueError('El género debe ser M o F')
        return v.upper() if v else v

    class Config:
        from_attributes = True

class AlumnoResponse(AlumnoBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True