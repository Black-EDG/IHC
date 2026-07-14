import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, ForeignKey, 
    text, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class TipoAlerta(str, enum.Enum):
    """Tipos de alertas del sistema según reglas de negocio"""
    SMS_3_FALTAS = 'sms_3_faltas'                 # 3 inasistencias acumuladas → SMS
    CITACION_5_FALTAS = 'citacion_5_faltas'       # 5 inasistencias acumuladas → PDF Citación
    JUSTIFICACION_BLOQUEADA = 'justificacion_bloqueada'  # 4ta falta consecutiva → Bloqueo virtual

class EstadoAlerta(str, enum.Enum):
    """Estados de entrega de la alerta"""
    ENVIADA = 'enviada'       # SMS enviado o PDF generado
    ENTREGADA = 'entregada'   # Confirmación de recepción o impresión
    FALLIDA = 'fallida'       # Error en el envío

class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    
    # CONEXIONES
    alumno_id = Column(
        Integer, 
        ForeignKey('alumnos.id', ondelete='RESTRICT'), 
        nullable=False,
        index=True,
        comment="Alumno que generó la alerta"
    )
    apoderado_id = Column(
        Integer, 
        ForeignKey('apoderados.id', ondelete='RESTRICT'), 
        nullable=False,
        index=True,
        comment="Apoderado que recibe la alerta"
    )
    
    # DATOS DE LA ALERTA
    tipo = Column(
        PG_ENUM(TipoAlerta, name="tipo_alerta", create_type=False),
        nullable=False,
        comment="Tipo de alerta: sms_3_faltas, citacion_5_faltas, justificacion_bloqueada"
    )
    estado = Column(
        PG_ENUM(EstadoAlerta, name="estado_alerta", create_type=False),
        server_default=text("'enviada'"),
        nullable=False
    )
    detalle = Column(
        Text, 
        nullable=True,
        comment="Contenido del SMS o detalle de la citación"
    )
    pdf_citacion_url = Column(
        String(255), 
        nullable=True,
        comment="Ruta del PDF de citación generado (solo para citacion_5_faltas)"
    )
    
    # FECHAS
    creado_en = Column(
        DateTime, 
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Fecha de creación/generación de la alerta"
    )
    entregado_en = Column(
        DateTime, 
        nullable=True,
        comment="Fecha de entrega efectiva (SMS confirmado o PDF impreso)"
    )
    
    # CONSTRAINTS
    __table_args__ = (
        Index("idx_alertas_alumno", "alumno_id"),
        Index("idx_alertas_apoderado", "apoderado_id"),
        Index("idx_alertas_tipo_estado", "tipo", "estado"),
        Index("idx_alertas_fecha", "creado_en"),
    )
    
    # RELACIONES
    alumno = relationship(
        "Alumno", 
        back_populates="alertas", 
        lazy="selectin",
        foreign_keys=[alumno_id]
    )
    apoderado = relationship(
        "Apoderado", 
        back_populates="alertas", 
        lazy="selectin",
        foreign_keys=[apoderado_id]
    )
    
    # ═══════════════════════════════════════════════════════════
    # PROPIEDADES CALCULADAS
    # ═══════════════════════════════════════════════════════════
    
    @property
    def es_sms(self) -> bool:
        """Verifica si es una alerta por SMS"""
        return self.tipo == TipoAlerta.SMS_3_FALTAS
    
    @property
    def es_citacion(self) -> bool:
        """Verifica si es una alerta de citación (PDF)"""
        return self.tipo == TipoAlerta.CITACION_5_FALTAS
    
    @property
    def es_bloqueo_justificacion(self) -> bool:
        """Verifica si es una alerta de bloqueo de justificación virtual"""
        return self.tipo == TipoAlerta.JUSTIFICACION_BLOQUEADA
    
    @property
    def fue_enviada(self) -> bool:
        """Verifica si la alerta fue enviada"""
        return self.estado == EstadoAlerta.ENVIADA
    
    @property
    def fue_entregada(self) -> bool:
        """Verifica si la alerta fue entregada/confirmada"""
        return self.estado == EstadoAlerta.ENTREGADA
    
    @property
    def fue_fallida(self) -> bool:
        """Verifica si la alerta falló"""
        return self.estado == EstadoAlerta.FALLIDA
    
    @property
    def dias_desde_envio(self) -> int:
        """Días transcurridos desde que se generó la alerta"""
        from datetime import date
        delta = date.today() - self.creado_en.date()
        return delta.days
    
    @property
    def mensaje_sms(self) -> str:
        """
        Genera el texto del SMS según el tipo de alerta.
        En producción, esto se enviaría por Twilio, Infobip, etc.
        """
        if not self.alumno:
            return "Alerta del colegio"
        
        nombre_alumno = self.alumno.nombre_completo
        grado = self.alumno.grado_seccion
        
        mensajes = {
            TipoAlerta.SMS_3_FALTAS: (
                f"COLEGIO: ATENCION. {nombre_alumno} de {grado} "
                f"acumula 3 inasistencias. Por favor comunicarse con el tutor. "
                f"Evite llegar al 30% de faltas para no perder el año."
            ),
            TipoAlerta.CITACION_5_FALTAS: (
                f"COLEGIO: URGENTE. {nombre_alumno} de {grado} "
                f"acumula 5 inasistencias. Se ha generado una citacion. "
                f"Acercarse a Direccion en los proximos 3 dias habiles."
            ),
            TipoAlerta.JUSTIFICACION_BLOQUEADA: (
                f"COLEGIO: AVISO. {nombre_alumno} de {grado} "
                f"ha alcanzado el limite de 3 justificaciones virtuales. "
                f"La proxima justificacion debe realizarla presencialmente en el colegio."
            )
        }
        return mensajes.get(self.tipo, "Alerta del colegio")
    
    def marcar_como_entregada(self) -> None:
        """Marca la alerta como entregada/confirmada"""
        self.estado = EstadoAlerta.ENTREGADA
        self.entregado_en = datetime.now()
    
    def marcar_como_fallida(self, motivo: str = None) -> None:
        """Marca la alerta como fallida"""
        self.estado = EstadoAlerta.FALLIDA
        if motivo:
            self.detalle = f"{self.detalle} | ERROR: {motivo}" if self.detalle else f"ERROR: {motivo}"
    
    def to_response(self) -> dict:
        """Formatea la alerta para respuesta API"""
        return {
            "id": self.id,
            "alumno_id": self.alumno_id,
            "alumno_nombre": self.alumno.nombre_completo if self.alumno else "Desconocido",
            "alumno_grado": self.alumno.grado_seccion if self.alumno else "",
            "apoderado_id": self.apoderado_id,
            "apoderado_nombre": self.apoderado.nombre_completo if self.apoderado else "Desconocido",
            "apoderado_celular": self.apoderado.celular if self.apoderado else "",
            "tipo": self.tipo.value,
            "tipo_legible": self._tipo_legible(),
            "estado": self.estado.value,
            "estado_legible": self._estado_legible(),
            "mensaje_sms": self.mensaje_sms,
            "detalle": self.detalle,
            "pdf_citacion_url": self.pdf_citacion_url,
            "dias_desde_envio": self.dias_desde_envio,
            "creado_en": self.creado_en.isoformat(),
            "entregado_en": self.entregado_en.isoformat() if self.entregado_en else None
        }
    
    def _tipo_legible(self) -> str:
        """Traduce el tipo de alerta a español"""
        traducciones = {
            'sms_3_faltas': 'SMS - 3 Inasistencias',
            'citacion_5_faltas': 'Citación PDF - 5 Inasistencias',
            'justificacion_bloqueada': 'Bloqueo de Justificación Virtual'
        }
        return traducciones.get(self.tipo.value, self.tipo.value)
    
    def _estado_legible(self) -> str:
        """Traduce el estado a español"""
        traducciones = {
            'enviada': 'Enviada',
            'entregada': 'Entregada',
            'fallida': 'Fallida'
        }
        return traducciones.get(self.estado.value, self.estado.value)
    
    def __repr__(self):
        return f"<Alerta {self.tipo.value} - Alumno {self.alumno_id} - {self.estado.value}>"