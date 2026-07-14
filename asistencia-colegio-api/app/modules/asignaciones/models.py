import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, 
    text, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class TipoResponsabilidad(str, enum.Enum):
    """Tipos de responsabilidad en el aula según normativa peruana"""
    DOCENTE_CURSO = 'docente_curso'       # Profesor que dicta una materia
    TUTOR_SECCION = 'tutor_seccion'       # Profesor tutor de una sección
    AUXILIAR_GRADO = 'auxiliar_grado'     # Auxiliar de educación por grado

class AsignacionAula(Base):
    __tablename__ = "asignaciones_aulas"

    id = Column(Integer, primary_key=True, index=True)
    
    # CONEXIONES FUNDAMENTALES
    usuario_id = Column(
        Integer, 
        ForeignKey('usuarios.id', ondelete='RESTRICT'), 
        nullable=False,
        index=True,
        comment="Profesor, Tutor o Auxiliar asignado"
    )
    aula_id = Column(
        Integer, 
        ForeignKey('aulas.id', ondelete='RESTRICT'), 
        nullable=False,
        index=True,
        comment="Aula donde ejerce su función"
    )
    curso_id = Column(
        Integer, 
        ForeignKey('cursos.id', ondelete='RESTRICT'), 
        nullable=True,
        comment="Curso que dicta. NULL si es Tutor o Auxiliar"
    )
    
    # TIPO DE RESPONSABILIDAD
    tipo_cargo = Column(
        PG_ENUM(TipoResponsabilidad, name="tipo_responsabilidad", create_type=False),
        nullable=False,
        comment="Rol que cumple en esta aula: docente_curso, tutor_seccion, auxiliar_grado"
    )
    
    # FECHA DE CREACIÓN
    creado_en = Column(
        DateTime, 
        server_default=text("CURRENT_TIMESTAMP")
    )
    
    # CONSTRAINTS
    __table_args__ = (
        # Regla de oro: No se puede asignar el mismo curso al mismo salón dos veces
        UniqueConstraint(
            'aula_id', 'curso_id', 'tipo_cargo',
            name="unica_asignacion_curso_aula"
        ),
        # Índices para carga rápida cuando el profesor inicia sesión
        Index("idx_asignaciones_usuario", "usuario_id"),
        Index("idx_asignaciones_aula", "aula_id"),
        Index("idx_asignaciones_tipo", "tipo_cargo"),
        Index("idx_asignaciones_usuario_tipo", "usuario_id", "tipo_cargo"),
    )
    
    # RELACIONES
    usuario = relationship(
        "Usuario", 
        back_populates="asignaciones", 
        lazy="selectin",
        foreign_keys=[usuario_id]
    )
    aula = relationship(
        "Aula", 
        back_populates="asignaciones", 
        lazy="selectin",
        foreign_keys=[aula_id]
    )
    curso = relationship(
        "Curso", 
        back_populates="asignaciones", 
        lazy="selectin",
        foreign_keys=[curso_id]
    )
    
    # ═══════════════════════════════════════════════════════════
    # PROPIEDADES CALCULADAS
    # ═══════════════════════════════════════════════════════════
    
    @property
    def es_docente(self) -> bool:
        """Verifica si es una asignación de tipo docente de curso"""
        return self.tipo_cargo == TipoResponsabilidad.DOCENTE_CURSO
    
    @property
    def es_tutor(self) -> bool:
        """Verifica si es una asignación de tipo tutor de sección"""
        return self.tipo_cargo == TipoResponsabilidad.TUTOR_SECCION
    
    @property
    def es_auxiliar(self) -> bool:
        """Verifica si es una asignación de tipo auxiliar de grado"""
        return self.tipo_cargo == TipoResponsabilidad.AUXILIAR_GRADO
    
    @property
    def nombre_completo_asignacion(self) -> str:
        """Retorna un nombre legible de la asignación"""
        usuario_nombre = self.usuario.nombre_completo if self.usuario else f"Usuario {self.usuario_id}"
        aula_nombre = self.aula.nombre_corto if self.aula else f"Aula {self.aula_id}"
        
        if self.es_docente:
            curso_nombre = self.curso.nombre if self.curso else f"Curso {self.curso_id}"
            return f"{usuario_nombre} → {curso_nombre} en {aula_nombre}"
        elif self.es_tutor:
            return f"{usuario_nombre} → Tutor de {aula_nombre}"
        elif self.es_auxiliar:
            return f"{usuario_nombre} → Auxiliar de {aula_nombre}"
        return f"{usuario_nombre} → {self.tipo_cargo.value} en {aula_nombre}"
    
    @property
    def puede_pasar_asistencia(self) -> bool:
        """
        Verifica si esta asignación permite pasar asistencia.
        - Docentes: Sí, en su curso
        - Auxiliares: Sí, asistencia general
        - Tutores: No directamente (solo consulta)
        """
        return self.tipo_cargo in [TipoResponsabilidad.DOCENTE_CURSO, TipoResponsabilidad.AUXILIAR_GRADO]
    
    def to_card_response(self) -> dict:
        """Formatea la asignación para mostrarla en una tarjeta"""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "usuario_nombre": self.usuario.nombre_completo if self.usuario else "Sin asignar",
            "usuario_dni": self.usuario.dni if self.usuario else None,
            "aula_id": self.aula_id,
            "aula_nombre": self.aula.nombre_corto if self.aula else f"Aula {self.aula_id}",
            "aula_completa": self.aula.nombre_completo if self.aula else None,
            "curso_id": self.curso_id,
            "curso_nombre": self.curso.nombre if self.curso else None,
            "tipo_cargo": self.tipo_cargo.value,
            "tipo_cargo_legible": self._tipo_cargo_legible(),
            "puede_pasar_asistencia": self.puede_pasar_asistencia,
            "grado": self.aula.grado if self.aula else None,
            "anio_escolar": self.aula.anio_escolar if self.aula else None
        }
    
    def _tipo_cargo_legible(self) -> str:
        """Retorna el tipo de cargo en español legible"""
        traducciones = {
            'docente_curso': 'Docente de Curso',
            'tutor_seccion': 'Tutor de Sección',
            'auxiliar_grado': 'Auxiliar de Grado'
        }
        return traducciones.get(self.tipo_cargo.value, self.tipo_cargo.value)
    
    def __repr__(self):
        return f"<Asignacion {self.nombre_completo_asignacion}>"