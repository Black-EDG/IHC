from pydantic import BaseModel, Field
from datetime import datetime, date

class AlumnoBase(BaseModel):
    dni: str = Field(..., min_length=8, max_length=8, description="DNI del estudiante")
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    fecha_nacimiento: date
    aula_id: int = Field(..., description="ID del salón asignado")
    apoderado_id: int = Field(..., description="ID del apoderado a cargo")

    class Config:
        from_attributes = True

class AlumnoCreate(AlumnoBase):
    pass

class AlumnoResponse(AlumnoBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True