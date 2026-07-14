import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, 
    text, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class EstadoTramiteJustificacion(str, enum.Enum):
    """Estados del trámite de justificación"""
    PENDIENTE = 'pendiente'
    APROBADA = 'aprobada'
    RECHAZADA = 'rechazada'

class Justificacion(Base):
    __tablename__ = "justificaciones"

    id = Column(Integer, primary_key=True, index=True)
    
    # CONEXIÓN DIRECTA CON LA FALTA
    asistencia_id = Column(
        Integer, 
        ForeignKey('asistencias.id', ondelete='CASCADE'), 
        unique=True,
        nullable=False,
        index=True,
        comment="Falta que se está justificando"
    )
    
    # DATOS DE LA JUSTIFICACIÓN
    motivo = Column(
        Text, 
        nullable=False,
        comment="Motivo escrito por el padre: 'Mi hijo amaneció con fiebre alta'"
    )
    archivo_sustento_url = Column(
        String(255), 
        nullable=True,
        comment="Ruta de la foto del certificado médico o nota escrita a mano"
    )
    
    # ESTADO DEL TRÁMITE
    estado = Column(
        PG_ENUM(EstadoTramiteJustificacion, name="estado_tramite_justificacion", create_type=False),
        server_default=text("'pendiente'"),
        nullable=False
    )
    observacion_auxiliar = Column(
        String(255), 
        nullable=True,
        comment="Por qué el auxiliar la aprobó o rechazó"
    )
    
    # METADATOS
    creado_en = Column(
        DateTime, 
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Fecha en que el padre envió la justificación"
    )
    
    # CONSTRAINTS
    __table_args__ = (
        CheckConstraint(
            "char_length(motivo) >= 10",
            name="check_motivo_minimo_10_caracteres"
        ),
    )
    
    # RELACIONES
    asistencia = relationship(
        "Asistencia", 
        back_populates="justificacion", 
        lazy="selectin",
        foreign_keys=[asistencia_id]
    )
    
    # ═══════════════════════════════════════════════════════════
    # PROPIEDADES CALCULADAS
    # ═══════════════════════════════════════════════════════════
    
    @property
    def esta_pendiente(self) -> bool:
        """Verifica si la justificación está pendiente de revisión"""
        return self.estado == EstadoTramiteJustificacion.PENDIENTE
    
    @property
    def esta_aprobada(self) -> bool:
        """Verifica si la justificación fue aprobada"""
        return self.estado == EstadoTramiteJustificacion.APROBADA
    
    @property
    def esta_rechazada(self) -> bool:
        """Verifica si la justificación fue rechazada"""
        return self.estado == EstadoTramiteJustificacion.RECHAZADA
    
    @property
    def tiene_sustento(self) -> bool:
        """Verifica si se adjuntó un archivo de sustento"""
        return self.archivo_sustento_url is not None and len(self.archivo_sustento_url) > 0
    
    @property
    def es_virtual(self) -> bool:
        """
        Determina si esta justificación fue enviada virtualmente (desde la app).
        Todas las justificaciones creadas desde la API son virtuales.
        Las presenciales se registran directamente en el colegio sin usar este flujo.
        """
        return True  # Por defecto, todas las creadas por API son virtuales
    
    @property
    def dias_desde_creacion(self) -> int:
        """Calcula cuántos días han pasado desde que se creó la justificación"""
        from datetime import date
        delta = date.today() - self.creado_en.date()
        return delta.days
    
    def aprobar(self, observacion: str = None) -> None:
        """
        Aprueba la justificación y actualiza el estado de la asistencia a 'justificado'.
        Solo puede ser ejecutado por el Auxiliar.
        """
        self.estado = EstadoTramiteJustificacion.APROBADA
        if observacion:
            self.observacion_auxiliar = observacion
        
        # Actualizar el estado de la asistencia a 'justificado'
        if self.asistencia:
            from app.modules.asistencias.models import EstadoAsistencia
            self.asistencia.estado = EstadoAsistencia.JUSTIFICADO
    
    def rechazar(self, observacion: str) -> None:
        """
        Rechaza la justificación.
        La falta permanece como 'ausente'.
        """
        self.estado = EstadoTramiteJustificacion.RECHAZADA
        self.observacion_auxiliar = observacion
    
    def to_response(self) -> dict:
        """Formatea la justificación para respuesta API"""
        alumno_nombre = "Desconocido"
        alumno_dni = ""
        fecha_falta = None
        aula = ""
        
        if self.asistencia:
            if self.asistencia.alumno:
                alumno_nombre = self.asistencia.alumno.nombre_completo
                alumno_dni = self.asistencia.alumno.dni
            fecha_falta = self.asistencia.fecha
            if self.asistencia.aula:
                aula = self.asistencia.aula.nombre_corto
        
        return {
            "id": self.id,
            "asistencia_id": self.asistencia_id,
            "alumno": alumno_nombre,
            "alumno_dni": alumno_dni,
            "fecha_falta": fecha_falta.isoformat() if fecha_falta else None,
            "aula": aula,
            "motivo": self.motivo,
            "tiene_sustento": self.tiene_sustento,
            "archivo_sustento_url": self.archivo_sustento_url,
            "estado": self.estado.value,
            "observacion_auxiliar": self.observacion_auxiliar,
            "dias_desde_creacion": self.dias_desde_creacion,
            "creado_en": self.creado_en.isoformat()
        }
    
    def __repr__(self):
        return f"<Justificacion {self.id} - Asistencia {self.asistencia_id} - {self.estado.value}>"