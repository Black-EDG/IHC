from sqlalchemy import Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    
    nombre = Column(
        String(100), 
        unique=True, 
        nullable=False,
        comment="Nombre del curso: Matemática, Comunicación, Inglés, etc."
    )
    
    descripcion = Column(
        Text, 
        nullable=True,
        comment="Descripción opcional: competencias, objetivos del curso"
    )
    
    creado_en = Column(
        DateTime, 
        server_default=text("CURRENT_TIMESTAMP")
    )
    
    # RELACIONES
    asignaciones = relationship(
        "AsignacionAula", 
        back_populates="curso", 
        lazy="selectin",
        foreign_keys="AsignacionAula.curso_id"
    )
    
    asistencias = relationship(
        "Asistencia", 
        back_populates="curso", 
        lazy="selectin",
        foreign_keys="Asistencia.curso_id"
    )
    
    # ═══════════════════════════════════════════════════════════
    # PROPIEDADES CALCULADAS
    # ═══════════════════════════════════════════════════════════
    
    @property
    def cantidad_docentes_asignados(self) -> int:
        """Retorna cuántos docentes están asignados a este curso"""
        if not self.asignaciones:
            return 0
        return len(set(a.usuario_id for a in self.asignaciones if a.tipo_cargo == 'docente_curso'))
    
    @property
    def cantidad_aulas_asignadas(self) -> int:
        """Retorna en cuántas aulas se dicta este curso"""
        if not self.asignaciones:
            return 0
        return len(set(a.aula_id for a in self.asignaciones if a.tipo_cargo == 'docente_curso'))
    
    @property
    def total_asistencias_registradas(self) -> int:
        """Retorna el total de registros de asistencia de este curso"""
        return len(self.asistencias) if self.asistencias else 0
    
    def docentes_por_aula(self) -> list:
        """
        Retorna un resumen de qué docente dicta este curso en cada aula.
        """
        if not self.asignaciones:
            return []
        
        resumen = []
        for asignacion in self.asignaciones:
            if asignacion.tipo_cargo == 'docente_curso' and asignacion.aula and asignacion.usuario:
                resumen.append({
                    "aula": asignacion.aula.nombre_corto if hasattr(asignacion.aula, 'nombre_corto') else f"Aula {asignacion.aula_id}",
                    "docente": asignacion.usuario.nombre_completo if hasattr(asignacion.usuario, 'nombre_completo') else f"Usuario {asignacion.usuario_id}",
                    "anio_escolar": asignacion.aula.anio_escolar if hasattr(asignacion.aula, 'anio_escolar') else None
                })
        
        return resumen
    
    def to_card_response(self) -> dict:
        """Formatea los datos del curso para mostrarlos en una tarjeta"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "cantidad_docentes": self.cantidad_docentes_asignados,
            "cantidad_aulas": self.cantidad_aulas_asignadas,
            "total_asistencias": self.total_asistencias_registradas
        }
    
    def __repr__(self):
        return f"<Curso {self.nombre}>"