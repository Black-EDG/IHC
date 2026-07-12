from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CursoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

class CursoCreate(CursoBase):
    pass

class CursoResponse(CursoBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True