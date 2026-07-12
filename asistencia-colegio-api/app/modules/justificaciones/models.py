import enum
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text, text
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class EstadoTramite(str, enum.Enum):
    pendiente = 'pendiente'
    aprobada = 'aprobada'
    rechazada = 'rechazada'

class Justificacion(Base):
    __tablename__ = "justificaciones"

    id = Column(Integer, primary_key=True, index=True)
    asistencia_id = Column(Integer, ForeignKey("asistencias.id", ondelete="CASCADE"), unique=True, nullable=False)
    motivo = Column(Text, nullable=False)
    archivo_sustento_url = Column(String(255), nullable=True)
    estado = Column(
        PG_ENUM(EstadoTramite, name="estado_tramite_justificacion", create_type=False),
        server_default=text("'pendiente'")
    )
    observacion_auxiliar = Column(String(255), nullable=True)
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))