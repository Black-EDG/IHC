from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.modules.justificaciones.models import EstadoTramite

class JustificacionBase(BaseModel):
    asistencia_id: int
    motivo: str = Field(..., min_length=10)
    archivo_sustento_url: Optional[str] = None
    estado: Optional[EstadoTramite] = EstadoTramite.pendiente
    observacion_auxiliar: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True

class JustificacionCreate(JustificacionBase):
    pass

class JustificacionUpdate(BaseModel):
    estado: EstadoTramite
    observacion_auxiliar: Optional[str] = Field(None, max_length=255)

class JustificacionResponse(JustificacionBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True