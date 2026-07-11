from pydantic import BaseModel, Field, field_validator
from typing import Optional

# 1. Esquema Base con los datos comunes y validaciones añadidas
class AulaBase(BaseModel):
    grado: int = Field(..., ge=1, le=5, description="Grado de secundaria (1 al 5)")
    seccion: str = Field(..., min_length=1, max_length=2, description="Sección del salón (Ej: A, B, C)")
    anio_escolar: int = Field(..., ge=2026, description="Año académico en curso")
    turno: Optional[str] = Field("mañana", max_length=10)

    # Convertidor automático: Asegura que la sección se guarde siempre en MAYÚSCULAS
    @field_validator('seccion')
    @classmethod
    def seccion_en_mayusculas(cls, v: str) -> str:
        return v.upper().strip()

    class Config:
        from_attributes = True

# 2. Esquema para CREAR un aula (Hereda todo del Base)
class AulaCreate(AulaBase):
    pass

# 3. Esquema para RESPONDER al Frontend (Devuelve el ID asignado)
class AulaResponse(AulaBase):
    id: int

    class Config:
        from_attributes = True