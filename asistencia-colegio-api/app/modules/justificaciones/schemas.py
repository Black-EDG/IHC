from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List

class JustificacionCreate(BaseModel):
    """
    Esquema para que el padre cree una justificación desde la App Familiar.
    """
    asistencia_id: int = Field(
        ..., 
        gt=0, 
        description="ID de la asistencia (falta) que se desea justificar"
    )
    motivo: str = Field(
        ..., 
        min_length=10, 
        max_length=500,
        description="Motivo de la inasistencia: 'Mi hijo amaneció con fiebre alta'"
    )
    archivo_sustento_url: Optional[str] = Field(
        None, 
        max_length=255,
        description="URL de la foto del certificado médico o nota escrita a mano"
    )
    
    @field_validator('motivo')
    @classmethod
    def limpiar_motivo(cls, v: str) -> str:
        """Limpia y capitaliza el motivo"""
        return v.strip()
    
    @field_validator('archivo_sustento_url')
    @classmethod
    def validar_url_sustento(cls, v: Optional[str]) -> Optional[str]:
        """Valida que la URL del sustento tenga un formato básico"""
        if v is not None:
            v = v.strip()
            if v and not (v.startswith('http://') or v.startswith('https://') or v.startswith('/')):
                raise ValueError("La URL del archivo debe comenzar con http://, https:// o /")
        return v

class JustificacionUpdateAuxiliar(BaseModel):
    """
    Esquema para que el Auxiliar apruebe o rechace una justificación.
    """
    estado: str = Field(
        ..., 
        description="Nuevo estado: aprobada o rechazada"
    )
    observacion_auxiliar: Optional[str] = Field(
        None, 
        max_length=255,
        description="Motivo de la aprobación o rechazo"
    )
    
    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        if v not in ['aprobada', 'rechazada']:
            raise ValueError("El estado debe ser 'aprobada' o 'rechazada'.")
        return v
    
    @field_validator('observacion_auxiliar')
    @classmethod
    def validar_observacion_rechazo(cls, v: Optional[str], info) -> Optional[str]:
        """
        Si se rechaza, la observación es obligatoria.
        No podemos acceder a 'estado' directamente aquí, se valida en el service.
        """
        return v.strip() if v else v

class JustificacionResponse(BaseModel):
    """Respuesta completa de una justificación"""
    id: int
    asistencia_id: int
    alumno: str
    alumno_dni: str
    fecha_falta: Optional[str]
    aula: str
    motivo: str
    tiene_sustento: bool
    archivo_sustento_url: Optional[str]
    estado: str
    observacion_auxiliar: Optional[str]
    dias_desde_creacion: int
    creado_en: str
    
    class Config:
        from_attributes = True

class JustificacionCardResponse(BaseModel):
    """Respuesta resumida para listados"""
    id: int
    asistencia_id: int
    alumno: str
    fecha_falta: Optional[str]
    aula: str
    motivo: str
    estado: str
    dias_desde_creacion: int
    
    class Config:
        from_attributes = True

class VerificarJustificacionesVirtualesResponse(BaseModel):
    """
    Respuesta que indica si un alumno puede seguir justificando virtualmente.
    """
    alumno_id: int
    alumno_nombre: str
    faltas_consecutivas: int
    justificaciones_virtuales_usadas: int
    justificaciones_virtuales_disponibles: int
    puede_justificar_virtualmente: bool
    mensaje: str
    
    class Config:
        from_attributes = True

class EstadisticasJustificacionesResponse(BaseModel):
    """Estadísticas generales de justificaciones"""
    total_pendientes: int
    total_aprobadas: int
    total_rechazadas: int
    total_general: int
    porcentaje_aprobacion: float
    fecha_consulta: date
    
    class Config:
        from_attributes = True