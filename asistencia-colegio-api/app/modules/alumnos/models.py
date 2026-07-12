from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, text, CheckConstraint
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base
import enum

class EstadoAlumno(str, enum.Enum):
    matriculado = 'matriculado'
    trasladado = 'trasladado'
    retirado = 'retirado'

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(8), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    genero = Column(String(1), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    
    aula_id = Column(Integer, ForeignKey("aulas.id", ondelete="RESTRICT"), nullable=False)
    apoderado_id = Column(Integer, ForeignKey("apoderados.id", ondelete="RESTRICT"), nullable=False)
    
    estado = Column(
        PG_ENUM(EstadoAlumno, name="estado_alumno", create_type=False),
        server_default=text("'matriculado'"),
        nullable=False
    )
    
    suspendido_desde = Column(Date, nullable=True)
    suspendido_hasta = Column(Date, nullable=True)
    
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint('genero IN (\'M\', \'F\')', name='check_genero_valido'),
        CheckConstraint('suspendido_desde <= suspendido_hasta', name='check_fechas_suspension'),
    )