from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List

class AulaBase(BaseModel):
    """Campos base compartidos para el aula"""
    grado: int = Field(..., ge=1, le=5, description="Grado: 1, 2, 3, 4, 5")
    seccion: str = Field(..., min_length=1, max_length=2, description="Sección: A, B, C, D, E")
    anio_escolar: int = Field(..., ge=2024, le=2100, description="Año escolar: 2026, 2027, etc.")
    turno: str = Field('mañana', description="Turno: mañana, tarde, noche")
    
    @field_validator('seccion')
    @classmethod
    def capitalizar_seccion(cls, v: str) -> str:
        """Convierte la sección a mayúscula"""
        return v.strip().upper()
    
    @field_validator('turno')
    @classmethod
    def validar_turno(cls, v: str) -> str:
        """Valida que el turno sea uno de los permitidos"""
        turnos_validos = ['mañana', 'tarde', 'noche']
        v = v.lower().strip()
        if v not in turnos_validos:
            raise ValueError(f"Turno '{v}' no válido. Opciones: {', '.join(turnos_validos)}")
        return v

    class Config:
        from_attributes = True

class AulaCreate(AulaBase):
    """Esquema para crear una nueva aula"""
    pass

class AulaUpdate(BaseModel):
    """Esquema para actualizar un aula (solo turno es modificable)"""
    turno: Optional[str] = Field(None, description="Turno: mañana, tarde, noche")
    
    @field_validator('turno')
    @classmethod
    def validar_turno(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        turnos_validos = ['mañana', 'tarde', 'noche']
        v = v.lower().strip()
        if v not in turnos_validos:
            raise ValueError(f"Turno '{v}' no válido. Opciones: {', '.join(turnos_validos)}")
        return v
    
    class Config:
        from_attributes = True

class AulaResponse(BaseModel):
    """Respuesta completa con datos del aula"""
    id: int
    grado: int
    seccion: str
    anio_escolar: int
    turno: str
    nombre_completo: str
    nombre_corto: str
    cantidad_alumnos: int
    cantidad_total_alumnos: int
    tiene_tutor: bool
    tiene_auxiliar: bool
    es_ultimo_grado: bool
    docentes_asignados: list = []
    creado_en: datetime
    
    class Config:
        from_attributes = True

class AulaCardResponse(BaseModel):
    """Respuesta resumida para tarjetas en la UI"""
    id: int
    nombre_completo: str
    nombre_corto: str
    grado: int
    seccion: str
    anio_escolar: int
    turno: str
    cantidad_alumnos: int
    tiene_tutor: bool
    tiene_auxiliar: bool
    es_ultimo_grado: bool
    docentes_count: int
    
    class Config:
        from_attributes = True

class AlumnoEnAulaResponse(BaseModel):
    """Respuesta de alumno dentro del contexto de un aula"""
    id: int
    dni: str
    nombre_completo: str
    genero: Optional[str]
    edad: int
    suspendido: bool
    apoderado: str
    
    class Config:
        from_attributes = True

class ListadoAulaResponse(BaseModel):
    """Respuesta completa del listado de un aula"""
    aula: AulaCardResponse
    total_alumnos: int
    alumnos: List[AlumnoEnAulaResponse] = []
    
    class Config:
        from_attributes = True

class AsistenciaAulaResponse(BaseModel):
    """Resumen de asistencia de un aula en una fecha"""
    fecha: str
    total_alumnos: int
    presentes: int
    ausentes: int
    tardes: int
    justificados: int
    sin_registro: int
    porcentaje_asistencia: float
    
    class Config:
        from_attributes = True

class CrearAulasPorGradoRequest(BaseModel):
    """Esquema para crear múltiples aulas por grado"""
    grado: int = Field(..., ge=1, le=5, description="Grado para el cual crear secciones")
    anio_escolar: int = Field(..., ge=2024, description="Año escolar")
    secciones: List[str] = Field(
        ..., 
        min_length=1, 
        max_length=10,
        description="Lista de secciones a crear: ['A', 'B', 'C', 'D', 'E']"
    )
    turno: str = Field('mañana', description="Turno para todas las secciones")
    
    @field_validator('secciones')
    @classmethod
    def validar_secciones(cls, v: List[str]) -> List[str]:
        """Capitaliza y valida las secciones"""
        return [s.strip().upper()[:2] for s in v]

class PromocionAulasResponse(BaseModel):
    """Respuesta del proceso de creación de aulas para el siguiente año"""
    anio_origen: int
    anio_destino: int
    aulas_creadas: int
    secciones_por_grado: dict = {}
    errores: List[str] = []
    fecha_proceso: datetime
    
    class Config:
        from_attributes = True

class AulaEstadisticasResponse(BaseModel):
    """Estadísticas de un aula específica"""
    aula: AulaCardResponse
    alumnos_matriculados: int
    alumnos_suspendidos: int
    alumnos_riesgo_inhabilitacion: int
    promedio_asistencia_semanal: float
    docentes_count: int
    tiene_tutor: bool
    tiene_auxiliar: bool
    
    class Config:
        from_attributes = True