import enum
from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, String, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class EstadoAsistencia(str, enum.Enum):
    presente = 'presente'
    tarde = 'tarde'
    falta_justificada = 'falta_justificada'
    falta_injustificada = 'falta_injustificada'

class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    
    # Mapeo de nuestro Enum nativo
    estado = Column(
        PG_ENUM(EstadoAsistencia, name="estado_asistencia", create_type=False),
        nullable=False
    )
    
    observacion = Column(String(255), nullable=True) # Para poner cosas como "Llegó con justificación médica"
    
    # Llaves foráneas obligatorias
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False) # Quién la tomó
    
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # Restricción brutal: Un alumno solo tiene un registro de asistencia por día
    __table_args__ = (
        UniqueConstraint('alumno_id', 'fecha', name='unico_alumno_por_fecha'),
    )