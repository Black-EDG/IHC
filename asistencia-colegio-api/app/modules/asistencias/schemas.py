from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from app.modules.asistencias.models import EstadoAsistencia

class AsistenciaBase(BaseModel):
    alumno_id: int
    usuario_id: int
    curso_id: Optional[int] = None
    fecha: Optional[date] = None
    estado: EstadoAsistencia
    observacion: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True

class AsistenciaCreate(AsistenciaBase):
    pass

class AsistenciaResponse(AsistenciaBase):
    id: int
    fecha: date
    creado_en: datetime

    class Config:
        from_attributes = True