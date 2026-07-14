import enum
from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, 
    text, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class EstadoAsistencia(str, enum.Enum):
    """Estados de asistencia en el colegio peruano"""
    PRESENTE = 'presente'
    AUSENTE = 'ausente'
    TARDE = 'tarde'
    JUSTIFICADO = 'justificado'

class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(Integer, primary_key=True, index=True)
    
    # CONEXIONES FUNDAMENTALES
    alumno_id = Column(
        Integer, 
        ForeignKey('alumnos.id', ondelete='RESTRICT'), 
        nullable=False,
        index=True
    )
    usuario_id = Column(
        Integer, 
        ForeignKey('usuarios.id', ondelete='RESTRICT'), 
        nullable=False,
        comment="Usuario que registró la asistencia (Auxiliar o Docente)"
    )
    curso_id = Column(
        Integer, 
        ForeignKey('cursos.id', ondelete='RESTRICT'), 
        nullable=True,
        comment="NULL = Asistencia General (Auxiliar). Con valor = Asistencia por Curso (Docente)"
    )
    aula_id = Column(
        Integer, 
        ForeignKey('aulas.id', ondelete='RESTRICT'), 
        nullable=False,
        index=True
    )
    
    # DATOS DE LA ASISTENCIA
    fecha = Column(
        Date, 
        nullable=False, 
        default=date.today,
        comment="Fecha del día de clases"
    )
    estado = Column(
        PG_ENUM(EstadoAsistencia, name="estado_asistencia", create_type=False),
        nullable=False
    )
    observacion = Column(
        String(255), 
        nullable=True,
        comment="Ej: 'Se retiró temprano', 'Entró en la segunda hora'"
    )
    
    # METADATOS
    creado_en = Column(
        DateTime, 
        server_default=text("CURRENT_TIMESTAMP")
    )
    
    # CONSTRAINTS
    __table_args__ = (
        # Restricción única: Un alumno no puede tener dos asistencias del mismo tipo el mismo día
        UniqueConstraint(
            'alumno_id', 'fecha', 'curso_id', 'aula_id',
            name="unica_asistencia_alumno_curso_dia"
        ),
        # Índices para reportes rápidos
        Index("idx_asistencias_alumno", "alumno_id"),
        Index("idx_asistencias_fecha", "fecha"),
        Index("idx_asistencias_aula_fecha", "aula_id", "fecha"),
        Index("idx_asistencias_alumno_fecha", "alumno_id", "fecha"),
        # Índice único parcial: Solo una asistencia general (curso_id IS NULL) por alumno por día
        Index(
            "idx_asistencia_general_unica",
            "alumno_id",
            "fecha",
            unique=True,
            postgresql_where=text("curso_id IS NULL")
        ),
    )
    
    # RELACIONES
    alumno = relationship(
        "Alumno", 
        back_populates="asistencias", 
        lazy="selectin",
        foreign_keys=[alumno_id]
    )
    usuario = relationship(
        "Usuario", 
        back_populates="asistencias_registradas", 
        lazy="selectin",
        foreign_keys=[usuario_id]
    )
    curso = relationship(
        "Curso", 
        back_populates="asistencias", 
        lazy="selectin",
        foreign_keys=[curso_id]
    )
    aula = relationship(
        "Aula", 
        back_populates="asistencias", 
        lazy="selectin",
        foreign_keys=[aula_id]
    )
    justificacion = relationship(
        "Justificacion", 
        back_populates="asistencia", 
        lazy="selectin",
        uselist=False,
        foreign_keys="Justificacion.asistencia_id"
    )
    
    # ═══════════════════════════════════════════════════════════
    # PROPIEDADES CALCULADAS
    # ═══════════════════════════════════════════════════════════
    
    @property
    def es_asistencia_general(self) -> bool:
        """Verifica si es asistencia general (tomada por el Auxiliar)"""
        return self.curso_id is None
    
    @property
    def es_asistencia_por_curso(self) -> bool:
        """Verifica si es asistencia por curso (tomada por el Docente)"""
        return self.curso_id is not None
    
    @property
    def es_falta(self) -> bool:
        """Verifica si la asistencia es una inasistencia"""
        return self.estado in [EstadoAsistencia.AUSENTE, EstadoAsistencia.JUSTIFICADO]
    
    @property
    def esta_justificada(self) -> bool:
        """Verifica si la falta tiene una justificación aprobada"""
        return self.estado == EstadoAsistencia.JUSTIFICADO
    
    @property
    def tiene_justificacion_pendiente(self) -> bool:
        """Verifica si hay una justificación pendiente de revisión"""
        if not self.justificacion:
            return False
        return self.justificacion.estado == 'pendiente'
    
    @property
    def puede_ser_justificada_virtualmente(self) -> bool:
        """
        Verifica si esta falta puede ser justificada virtualmente.
        Regla: Máximo 3 justificaciones virtuales consecutivas.
        """
        if not self.es_falta:
            return False
        if self.esta_justificada:
            return False
        return True
    
    def resumen_asistencia(self) -> dict:
        """Retorna un resumen legible de esta asistencia"""
        nombre_curso = self.curso.nombre if self.curso else "General"
        nombre_aula = self.aula.nombre_corto if self.aula else f"Aula {self.aula_id}"
        
        return {
            "id": self.id,
            "alumno": self.alumno.nombre_completo if self.alumno else f"Alumno {self.alumno_id}",
            "fecha": self.fecha.isoformat(),
            "estado": self.estado.value,
            "tipo": "General" if self.es_asistencia_general else f"Curso: {nombre_curso}",
            "aula": nombre_aula,
            "registrado_por": self.usuario.nombre_completo if self.usuario else "Sistema",
            "observacion": self.observacion,
            "justificada": self.esta_justificada
        }
    
    def __repr__(self):
        tipo = "General" if self.es_asistencia_general else f"Curso {self.curso_id}"
        return f"<Asistencia {self.alumno_id} - {self.fecha} - {self.estado.value} ({tipo})>"