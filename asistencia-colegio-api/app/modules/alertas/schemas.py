from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional, List

class AlertaResponse(BaseModel):
    """Respuesta completa de una alerta"""
    id: int
    alumno_id: int
    alumno_nombre: str
    alumno_grado: str
    apoderado_id: int
    apoderado_nombre: str
    apoderado_celular: str
    tipo: str
    tipo_legible: str
    estado: str
    estado_legible: str
    mensaje_sms: str
    detalle: Optional[str]
    pdf_citacion_url: Optional[str]
    dias_desde_envio: int
    creado_en: str
    entregado_en: Optional[str]
    
    class Config:
        from_attributes = True

class AlertaCardResponse(BaseModel):
    """Respuesta resumida para listados"""
    id: int
    alumno_nombre: str
    alumno_grado: str
    apoderado_nombre: str
    tipo_legible: str
    estado_legible: str
    dias_desde_envio: int
    creado_en: str
    
    class Config:
        from_attributes = True

class DispararAlertasResponse(BaseModel):
    """
    Respuesta del proceso automático de disparo de alertas.
    Se ejecuta diariamente por un scheduler.
    """
    fecha_proceso: date
    total_alumnos_verificados: int
    alertas_sms_3_faltas: int
    alertas_citacion_5_faltas: int
    alertas_bloqueo_justificacion: int
    total_alertas_generadas: int
    errores: List[str] = []
    
    class Config:
        from_attributes = True

class MarcarEntregadaRequest(BaseModel):
    """Solicitud para marcar una alerta como entregada"""
    alerta_id: int = Field(..., gt=0)

class EstadisticasAlertasResponse(BaseModel):
    """Estadísticas generales de alertas"""
    total_sms_enviados: int
    total_citaciones_generadas: int
    total_bloqueos: int
    total_pendientes_entrega: int
    total_fallidas: int
    fecha_consulta: date
    
    class Config:
        from_attributes = True