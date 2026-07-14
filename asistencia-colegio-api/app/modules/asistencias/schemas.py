from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date, datetime
from typing import Optional, List
from app.modules.asistencias.models import EstadoAsistencia

class AsistenciaBase(BaseModel):
    """Campos base para registro de asistencia"""
    alumno_id: int = Field(..., gt=0, description="ID del alumno")
    estado: str = Field(..., description="Estado: presente, ausente, tarde, justificado")
    observacion: Optional[str] = Field(None, max_length=255, description="Observación opcional")
    
    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        estados_validos = [e.value for e in EstadoAsistencia]
        if v not in estados_validos:
            raise ValueError(f"Estado '{v}' no válido. Opciones: {', '.join(estados_validos)}")
        return v

    class Config:
        from_attributes = True

class AsistenciaIndividualCreate(AsistenciaBase):
    """Registrar asistencia de UN alumno (uso individual)"""
    pass

class AsistenciaMasivaCreate(BaseModel):
    """Registrar asistencia de TODOS los alumnos de un aula"""
    aula_id: int = Field(..., gt=0, description="ID del aula")
    curso_id: Optional[int] = Field(None, description="ID del curso. NULL = Asistencia General (Auxiliar)")
    fecha: date = Field(default_factory=date.today, description="Fecha de la asistencia")
    asistencias: List[AsistenciaBase] = Field(
        ..., 
        min_length=1, 
        description="Lista de asistencias de cada alumno"
    )
    
    @model_validator(mode='after')
    def validar_fecha(self):
        """La fecha no puede ser futura"""
        if self.fecha > date.today():
            raise ValueError("No se puede registrar asistencia para fechas futuras.")
        return self

class AsistenciaUpdate(BaseModel):
    """Actualizar una asistencia existente"""
    estado: str = Field(..., description="Nuevo estado: presente, ausente, tarde, justificado")
    observacion: Optional[str] = Field(None, max_length=255)
    
    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        estados_validos = [e.value for e in EstadoAsistencia]
        if v not in estados_validos:
            raise ValueError(f"Estado '{v}' no válido. Opciones: {', '.join(estados_validos)}")
        return v

class AsistenciaResponse(BaseModel):
    """Respuesta con datos de la asistencia"""
    id: int
    alumno_id: int
    usuario_id: int
    curso_id: Optional[int]
    aula_id: int
    fecha: date
    estado: str
    observacion: Optional[str]
    es_asistencia_general: bool
    es_asistencia_por_curso: bool
    es_falta: bool
    esta_justificada: bool
    creado_en: datetime
    
    class Config:
        from_attributes = True

class AsistenciaDetalleResponse(BaseModel):
    """Respuesta detallada con nombres"""
    id: int
    alumno: str
    alumno_dni: str
    fecha: date
    estado: str
    tipo: str
    aula: str
    registrado_por: str
    observacion: Optional[str]
    justificada: bool
    
    class Config:
        from_attributes = True

class ResumenAsistenciaAulaResponse(BaseModel):
    """Resumen de asistencia de un aula en una fecha"""
    aula_id: int
    aula_nombre: str
    fecha: date
    total_alumnos: int
    presentes: int
    ausentes: int
    tardes: int
    justificados: int
    sin_registro: int
    porcentaje_asistencia: float
    
    class Config:
        from_attributes = True

class ResumenAsistenciaAlumnoResponse(BaseModel):
    """Resumen de asistencias de un alumno en un período"""
    alumno_id: int
    alumno_nombre: str
    grado_seccion: str
    fecha_inicio: date
    fecha_fin: date
    total_registros: int
    presentes: int
    ausentes: int
    tardes: int
    justificados: int
    porcentaje_asistencia: float
    riesgo_inhabilitacion: bool
    faltas_consecutivas: int
    justificaciones_virtuales_disponibles: int
    
    class Config:
        from_attributes = True

class EstadisticasGeneralesResponse(BaseModel):
    """Estadísticas generales de asistencias"""
    fecha_consulta: date
    total_alumnos_matriculados: int
    total_asistencias_hoy: int
    presentes_hoy: int
    ausentes_hoy: int
    tardes_hoy: int
    justificados_hoy: int
    porcentaje_asistencia_hoy: float
    alumnos_riesgo_inhabilitacion: int