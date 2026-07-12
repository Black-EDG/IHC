from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.modules.asignaciones.models import TipoResponsabilidad

class AsignacionBase(BaseModel):
    usuario_id: int
    aula_id: int
    curso_id: Optional[int] = None
    tipo_cargo: TipoResponsabilidad

    class Config:
        from_attributes = True

class AsignacionCreate(AsignacionBase):
    pass

class AsignacionResponse(AsignacionBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True