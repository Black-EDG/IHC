from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
from app.modules.asignaciones.models import TipoResponsabilidad

class AsignacionBase(BaseModel):
    """Campos base para una asignación"""
    usuario_id: int = Field(..., gt=0, description="ID del usuario (Docente, Tutor o Auxiliar)")
    aula_id: int = Field(..., gt=0, description="ID del aula asignada")
    curso_id: Optional[int] = Field(None, description="ID del curso. NULL si es Tutor o Auxiliar")
    tipo_cargo: str = Field(..., description="Tipo: docente_curso, tutor_seccion, auxiliar_grado")
    
    @field_validator('tipo_cargo')
    @classmethod
    def validar_tipo_cargo(cls, v: str) -> str:
        tipos_validos = [t.value for t in TipoResponsabilidad]
        if v not in tipos_validos:
            raise ValueError(f"Tipo de cargo '{v}' no válido. Opciones: {', '.join(tipos_validos)}")
        return v
    
    @model_validator(mode='after')
    def validar_curso_segun_cargo(self):
        """
        Validaciones de negocio:
        - docente_curso: DEBE tener curso_id
        - tutor_seccion: NO debe tener curso_id
        - auxiliar_grado: NO debe tener curso_id
        """
        if self.tipo_cargo == 'docente_curso' and not self.curso_id:
            raise ValueError("Un docente de curso debe tener un curso asignado (curso_id requerido).")
        
        if self.tipo_cargo in ['tutor_seccion', 'auxiliar_grado'] and self.curso_id:
            raise ValueError(f"Un {self.tipo_cargo} no debe tener curso asignado (curso_id debe ser NULL).")
        
        return self

    class Config:
        from_attributes = True

class AsignacionCreate(AsignacionBase):
    """Esquema para crear una nueva asignación"""
    pass

class AsignacionUpdate(BaseModel):
    """Esquema para actualizar una asignación"""
    usuario_id: Optional[int] = Field(None, gt=0, description="Nuevo ID de usuario")
    aula_id: Optional[int] = Field(None, gt=0, description="Nuevo ID de aula")
    curso_id: Optional[int] = Field(None, description="Nuevo ID de curso")

    class Config:
        from_attributes = True

class AsignacionResponse(BaseModel):
    """Respuesta completa de una asignación"""
    id: int
    usuario_id: int
    usuario_nombre: str
    usuario_dni: Optional[str]
    aula_id: int
    aula_nombre: str
    aula_completa: Optional[str]
    curso_id: Optional[int]
    curso_nombre: Optional[str]
    tipo_cargo: str
    tipo_cargo_legible: str
    puede_pasar_asistencia: bool
    grado: Optional[int]
    anio_escolar: Optional[int]
    nombre_completo_asignacion: str
    creado_en: datetime
    
    class Config:
        from_attributes = True

class AsignacionCardResponse(BaseModel):
    """Respuesta resumida para tarjetas"""
    id: int
    usuario_id: int
    usuario_nombre: str
    aula_nombre: str
    curso_nombre: Optional[str]
    tipo_cargo_legible: str
    grado: Optional[int]
    anio_escolar: Optional[int]
    
    class Config:
        from_attributes = True

class DashboardDocenteResponse(BaseModel):
    """
    Respuesta completa del dashboard de un docente al iniciar sesión.
    Muestra todas sus asignaciones organizadas por tipo.
    """
    usuario_id: int
    usuario_nombre: str
    usuario_rol: str
    asignaciones_docente: List[AsignacionCardResponse] = []
    asignaciones_tutor: List[AsignacionCardResponse] = []
    asignaciones_auxiliar: List[AsignacionCardResponse] = []
    total_asignaciones: int
    
    class Config:
        from_attributes = True

class AsignacionMasivaRequest(BaseModel):
    """
    Esquema para asignar un docente a múltiples aulas para un mismo curso.
    Ejemplo: Profesor de Matemática para 1°A, 1°B, 1°C, 2°A, 2°B
    """
    usuario_id: int = Field(..., gt=0, description="ID del docente")
    curso_id: int = Field(..., gt=0, description="ID del curso que dicta")
    aulas_ids: List[int] = Field(
        ..., 
        min_length=1, 
        max_length=25,
        description="Lista de IDs de aulas donde dictará el curso"
    )
    tipo_cargo: str = Field('docente_curso', description="Tipo de asignación")
    
    @field_validator('tipo_cargo')
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        if v != 'docente_curso':
            raise ValueError("La asignación masiva solo aplica para docente_curso.")
        return v

class ResumenAulaResponse(BaseModel):
    """Resumen de todas las asignaciones de un aula"""
    aula_id: int
    aula_nombre: str
    grado: int
    seccion: str
    anio_escolar: int
    docentes: List[AsignacionCardResponse] = []
    tutor: Optional[AsignacionCardResponse] = None
    auxiliar: Optional[AsignacionCardResponse] = None
    total_docentes: int
    
    class Config:
        from_attributes = True