import enum
from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, String, text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class EstadoAsistencia(str, enum.Enum):
    presente = 'presente'
    ausente = 'ausente'
    tarde = 'tarde'
    justificado = 'justificado'

class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="RESTRICT"), nullable=True)
    
    fecha = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    estado = Column(
        PG_ENUM(EstadoAsistencia, name="estado_asistencia", create_type=False),
        nullable=False
    )
    observacion = Column(String(255), nullable=True)
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint('alumno_id', 'fecha', 'curso_id', name='unica_asistencia_alumno_dia'),
        Index('idx_asistencia_general_unica', 'alumno_id', 'fecha', unique=True, postgresql_where=(curso_id == None)),
    )