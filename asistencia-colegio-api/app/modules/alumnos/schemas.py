from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import date, datetime
from typing import Optional, List
from app.modules.alumnos.models import EstadoAlumno, GeneroAlumno

class AlumnoBase(BaseModel):
    """Campos base compartidos para el alumno"""
    dni: str = Field(..., min_length=8, max_length=8, pattern=r'^\d{8}$', description="DNI del alumno (8 dígitos)")
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres del alumno")
    apellidos: str = Field(..., min_length=2, max_length=100, description="Apellidos del alumno")
    genero: str = Field(..., pattern=r'^[MF]$', description="Género: M o F")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento (YYYY-MM-DD)")
    
    @field_validator('nombres', 'apellidos')
    @classmethod
    def capitalizar_nombres(cls, v: str) -> str:
        """Capitaliza correctamente nombres y apellidos"""
        return ' '.join(word.capitalize() for word in v.strip().split())
    
    @field_validator('fecha_nacimiento')
    @classmethod
    def validar_edad_minima(cls, v: date) -> date:
        """Valida que el alumno tenga al menos 10 años (edad mínima para secundaria)"""
        hoy = date.today()
        edad = hoy.year - v.year - ((hoy.month, hoy.day) < (v.month, v.day))
        
        if edad < 10:
            raise ValueError(f"El alumno debe tener al menos 10 años. Edad calculada: {edad} años.")
        if edad > 18:
            raise ValueError(f"Edad fuera del rango esperado para secundaria: {edad} años.")
        
        return v

    class Config:
        from_attributes = True

class AlumnoCreate(AlumnoBase):
    """Esquema para matricular un nuevo alumno"""
    aula_id: int = Field(..., gt=0, description="ID del aula donde se matricula")
    apoderado_id: int = Field(..., gt=0, description="ID del apoderado responsable")
    estado: Optional[str] = Field('matriculado', description="Estado inicial del alumno")
    
    @field_validator('estado')
    @classmethod
    def validar_estado_inicial(cls, v: str) -> str:
        """El estado inicial debe ser un valor válido del ENUM"""
        estados_validos = [e.value for e in EstadoAlumno]
        if v not in estados_validos:
            raise ValueError(f"Estado '{v}' no válido. Opciones: {', '.join(estados_validos)}")
        return v

class AlumnoUpdate(BaseModel):
    """Esquema para actualizar datos del alumno (todos opcionales)"""
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    genero: Optional[str] = Field(None, pattern=r'^[MF]$')
    fecha_nacimiento: Optional[date] = None
    aula_id: Optional[int] = Field(None, gt=0)
    apoderado_id: Optional[int] = Field(None, gt=0)
    estado: Optional[str] = None
    
    class Config:
        from_attributes = True

class SuspensionRequest(BaseModel):
    """Esquema para suspender a un alumno"""
    desde: date = Field(..., description="Fecha de inicio de suspensión (YYYY-MM-DD)")
    hasta: date = Field(..., description="Fecha de fin de suspensión (YYYY-MM-DD)")
    motivo: Optional[str] = Field(None, max_length=255, description="Motivo de la suspensión")
    
    @model_validator(mode='after')
    def validar_fechas_suspension(self):
        """Valida que las fechas de suspensión sean coherentes"""
        if self.desde > self.hasta:
            raise ValueError("La fecha de inicio no puede ser mayor a la fecha de fin.")
        
        if self.desde < date.today():
            raise ValueError("No se puede suspender con fecha anterior a hoy.")
        
        # Máximo 30 días de suspensión
        delta = (self.hasta - self.desde).days
        if delta > 30:
            raise ValueError(f"La suspensión no puede exceder los 30 días. Solicitado: {delta} días.")
        
        return self

class TrasladoRequest(BaseModel):
    """Esquema para trasladar a un alumno de aula"""
    nueva_aula_id: int = Field(..., gt=0, description="ID del aula de destino")
    motivo: Optional[str] = Field(None, max_length=255, description="Motivo del traslado")

class AlumnoCardResponse(BaseModel):
    """Respuesta resumida para tarjetas en la UI"""
    id: int
    dni: str
    nombre_completo: str
    genero: Optional[str]
    edad: int
    grado_seccion: str
    estado: str
    suspendido: bool
    dias_suspension_restantes: int
    apoderado_nombre: str
    apoderado_celular: Optional[str]
    
    class Config:
        from_attributes = True

class AlumnoResponse(BaseModel):
    """Respuesta completa con todos los datos del alumno"""
    id: int
    dni: str
    nombres: str
    apellidos: str
    nombre_completo: str
    genero: str
    fecha_nacimiento: date
    edad: int
    
    # Datos del aula
    aula_id: int
    grado_seccion: str
    
    # Datos del apoderado
    apoderado_id: int
    apoderado_nombre: Optional[str]
    apoderado_celular: Optional[str]
    apoderado_parentesco: Optional[str]
    
    # Estado y suspensiones
    estado: str
    suspendido_desde: Optional[date]
    suspendido_hasta: Optional[date]
    esta_suspendido: bool
    dias_suspension_restantes: int
    
    # Metadatos
    creado_en: datetime
    
    class Config:
        from_attributes = True

class AlumnoResumenAsistenciaResponse(BaseModel):
    """Resumen de asistencias para un alumno"""
    alumno_id: int
    alumno_nombre: str
    grado_seccion: str
    total_asistencias: int
    presentes: int
    ausentes: int
    tardes: int
    justificados: int
    porcentaje_asistencia: float
    riesgo_inhabilitacion: bool
    
    class Config:
        from_attributes = True

class PromocionMasivaResponse(BaseModel):
    """Respuesta del proceso de promoción masiva"""
    total_procesados: int
    promovidos: int
    graduados: int  # Alumnos de 5° que terminan
    no_promovidos: int  # Retirados o trasladados
    errores: List[str] = []
    fecha_proceso: datetime
    
    class Config:
        from_attributes = True

class AlumnoBusquedaResponse(BaseModel):
    """Respuesta resumida para búsquedas rápidas"""
    id: int
    dni: str
    nombre_completo: str
    grado_seccion: str
    estado: str
    apoderado_nombre: str
    
    class Config:
        from_attributes = True