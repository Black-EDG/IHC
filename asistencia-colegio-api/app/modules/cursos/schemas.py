from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List

class CursoBase(BaseModel):
    """Campos base compartidos para el curso"""
    nombre: str = Field(
        ..., 
        min_length=3, 
        max_length=100, 
        description="Nombre del curso: Matemática, Comunicación, Inglés, etc."
    )
    descripcion: Optional[str] = Field(
        None, 
        max_length=500,
        description="Descripción opcional del curso (competencias, objetivos)"
    )
    
    @field_validator('nombre')
    @classmethod
    def capitalizar_nombre(cls, v: str) -> str:
        """Capitaliza correctamente el nombre del curso"""
        # Quitar espacios extras y capitalizar primera letra de cada palabra
        return ' '.join(word.capitalize() for word in v.strip().split())
    
    @field_validator('descripcion')
    @classmethod
    def limpiar_descripcion(cls, v: Optional[str]) -> Optional[str]:
        """Limpia la descripción de espacios innecesarios"""
        if v is not None:
            return v.strip()
        return v

    class Config:
        from_attributes = True

class CursoCreate(CursoBase):
    """Esquema para crear un nuevo curso"""
    pass

class CursoUpdate(BaseModel):
    """Esquema para actualizar un curso (todos opcionales)"""
    nombre: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=100,
        description="Nuevo nombre del curso"
    )
    descripcion: Optional[str] = Field(
        None, 
        max_length=500,
        description="Nueva descripción del curso"
    )
    
    @field_validator('nombre')
    @classmethod
    def capitalizar_nombre(cls, v: Optional[str]) -> Optional[str]:
        """Capitaliza el nombre si se proporciona"""
        if v is not None:
            return ' '.join(word.capitalize() for word in v.strip().split())
        return v

    class Config:
        from_attributes = True

class DocentePorAulaResponse(BaseModel):
    """Respuesta de docente asignado a un curso en un aula"""
    aula: str
    docente: str
    anio_escolar: Optional[int]

    class Config:
        from_attributes = True

class CursoResponse(BaseModel):
    """Respuesta completa con datos del curso"""
    id: int
    nombre: str
    descripcion: Optional[str]
    cantidad_docentes_asignados: int
    cantidad_aulas_asignadas: int
    total_asistencias_registradas: int
    docentes_por_aula: List[DocentePorAulaResponse] = []
    creado_en: datetime

    class Config:
        from_attributes = True

class CursoCardResponse(BaseModel):
    """Respuesta resumida para tarjetas en la UI"""
    id: int
    nombre: str
    descripcion: Optional[str]
    cantidad_docentes: int
    cantidad_aulas: int
    total_asistencias: int

    class Config:
        from_attributes = True

class CursoBusquedaResponse(BaseModel):
    """Respuesta resumida para búsquedas rápidas"""
    id: int
    nombre: str
    cantidad_docentes: int

    class Config:
        from_attributes = True

class CursoCreateMultiple(BaseModel):
    """Esquema para crear múltiples cursos a la vez"""
    cursos: List[CursoCreate] = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Lista de cursos a crear"
    )