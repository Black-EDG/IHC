from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from app.modules.asistencias.models import EstadoAsistencia

class AsistenciaBase(BaseModel):
    fecha: Optional[date] = None # Si es None, el servicio le pondrá la fecha de hoy
    estado: EstadoAsistencia
    observacion: Optional[str] = Field(None, max_length=255)
    alumno_id: int
    usuario_id: int

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