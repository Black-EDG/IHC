import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class TipoResponsabilidad(str, enum.Enum):
    docente_curso = 'docente_curso'
    tutor_seccion = 'tutor_seccion'
    auxiliar_grado = 'auxiliar_grado'

class AsignacionAula(Base):
    __tablename__ = "asignaciones_aulas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    aula_id = Column(Integer, ForeignKey("aulas.id", ondelete="RESTRICT"), nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="RESTRICT"), nullable=True)
    tipo_cargo = Column(
        PG_ENUM(TipoResponsabilidad, name="tipo_responsabilidad", create_type=False),
        nullable=False
    )
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint('aula_id', 'curso_id', 'tipo_cargo', name='unica_asignacion_curso_aula'),
    )