import enum
from datetime import date
from sqlalchemy import (
    Column, Integer, SmallInteger, String, DateTime, 
    ForeignKey, text, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base

class TurnoAula(str, enum.Enum):
    """Turnos disponibles para las aulas en colegios peruanos"""
    MANANA = 'mañana'
    TARDE = 'tarde'
    NOCHE = 'noche'

class Aula(Base):
    __tablename__ = "aulas"

    id = Column(Integer, primary_key=True, index=True)
    
    # DATOS DEL AULA
    grado = Column(
        SmallInteger, 
        nullable=False,
        comment="Grado de secundaria: 1, 2, 3, 4, 5"
    )
    seccion = Column(
        String(2), 
        nullable=False,
        comment="Sección: A, B, C, D, E"
    )
    anio_escolar = Column(
        Integer, 
        nullable=False,
        comment="Año escolar: 2026, 2027, etc."
    )
    turno = Column(
        String(10), 
        server_default=text("'mañana'"),
        nullable=False,
        comment="Turno: mañana, tarde, noche"
    )
    
    # FECHA DE CREACIÓN
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    
    # CONSTRAINTS
    __table_args__ = (
        # Solo grados 1-5 (Secundaria en Perú)
        CheckConstraint(
            "grado >= 1 AND grado <= 5",
            name="check_grado_secundaria"
        ),
        # Evita duplicados: misma sección, mismo año
        UniqueConstraint(
            'grado', 'seccion', 'anio_escolar',
            name="unica_seccion_por_anio"
        ),
        # Validación de turno
        CheckConstraint(
            "turno IN ('mañana', 'tarde', 'noche')",
            name="check_turno_valido"
        ),
        # Índices para búsquedas frecuentes
        Index("idx_aulas_anio_escolar", "anio_escolar"),
        Index("idx_aulas_grado", "grado"),
        Index("idx_aulas_grado_seccion", "grado", "seccion", "anio_escolar"),
    )
    
    # RELACIONES
    alumnos = relationship(
        "Alumno", 
        back_populates="aula", 
        lazy="selectin",
        foreign_keys="Alumno.aula_id",
        primaryjoin="Aula.id == Alumno.aula_id"
    )
    
    asignaciones = relationship(
        "AsignacionAula", 
        back_populates="aula", 
        lazy="selectin",
        foreign_keys="AsignacionAula.aula_id"
    )
    
    asistencias = relationship(
        "Asistencia", 
        back_populates="aula", 
        lazy="selectin",
        foreign_keys="Asistencia.aula_id"
    )
    
    # ═══════════════════════════════════════════════════════════
    # PROPIEDADES CALCULADAS
    # ═══════════════════════════════════════════════════════════
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre formateado: '1° A - 2026 (mañana)'"""
        return f"{self.grado}° {self.seccion} - {self.anio_escolar} ({self.turno})"
    
    @property
    def nombre_corto(self) -> str:
        """Retorna el nombre corto: '1° A'"""
        return f"{self.grado}° {self.seccion}"
    
    @property
    def cantidad_alumnos(self) -> int:
        """Cantidad de alumnos actualmente en esta aula"""
        if not self.alumnos:
            return 0
        # Solo contar alumnos matriculados
        from app.modules.alumnos.models import EstadoAlumno
        return sum(1 for a in self.alumnos if a.estado == EstadoAlumno.MATRICULADO)
    
    @property
    def cantidad_total_alumnos(self) -> int:
        """Cantidad total de alumnos (incluye retirados y trasladados)"""
        return len(self.alumnos) if self.alumnos else 0
    
    @property
    def tiene_tutor(self) -> bool:
        """Verifica si el aula tiene un tutor asignado"""
        if not self.asignaciones:
            return False
        return any(a.tipo_cargo == 'tutor_seccion' for a in self.asignaciones)
    
    @property
    def tiene_auxiliar(self) -> bool:
        """Verifica si el aula tiene un auxiliar asignado"""
        if not self.asignaciones:
            return False
        return any(a.tipo_cargo == 'auxiliar_grado' for a in self.asignaciones)
    
    @property
    def docentes_asignados(self) -> list:
        """Retorna la lista de docentes asignados a esta aula"""
        if not self.asignaciones:
            return []
        return [
            {
                "usuario_id": a.usuario_id,
                "nombre": a.usuario.nombre_completo if a.usuario else "Sin asignar",
                "curso": a.curso.nombre if a.curso else "Tutoría/General",
                "tipo": a.tipo_cargo
            }
            for a in self.asignaciones 
            if a.tipo_cargo == 'docente_curso'
        ]
    
    @property
    def es_ultimo_grado(self) -> bool:
        """Verifica si es 5° grado (último año de secundaria)"""
        return self.grado == 5
    
    @property
    def grado_siguiente(self) -> int:
        """Retorna el siguiente grado o None si es 5°"""
        return self.grado + 1 if self.grado < 5 else None
    
    # ═══════════════════════════════════════════════════════════
    # MÉTODOS DE NEGOCIO
    # ═══════════════════════════════════════════════════════════
    
    def listado_alumnos(self, solo_activos: bool = True) -> list:
        """
        Retorna el listado de alumnos del aula ordenado alfabéticamente.
        
        Args:
            solo_activos: Si True, solo retorna alumnos matriculados
        """
        if not self.alumnos:
            return []
        
        alumnos_lista = self.alumnos
        if solo_activos:
            from app.modules.alumnos.models import EstadoAlumno
            alumnos_lista = [a for a in alumnos_lista if a.estado == EstadoAlumno.MATRICULADO]
        
        # Ordenar por apellidos
        alumnos_lista.sort(key=lambda x: x.apellidos)
        
        return [
            {
                "id": a.id,
                "dni": a.dni,
                "nombre_completo": a.nombre_completo,
                "genero": a.genero.value if a.genero else None,
                "edad": a.edad,
                "suspendido": a.esta_suspendido,
                "apoderado": a.apoderado.nombre_completo if a.apoderado else "Sin apoderado"
            }
            for a in alumnos_lista
        ]
    
    def resumen_asistencias_fecha(self, fecha: date = None) -> dict:
        """
        Calcula el resumen de asistencias del aula en una fecha específica.
        Si no se especifica fecha, toma la fecha actual.
        """
        if not fecha:
            fecha = date.today()
        
        if not self.asistencias:
            return {
                "fecha": fecha,
                "total_alumnos": self.cantidad_alumnos,
                "presentes": 0,
                "ausentes": 0,
                "tardes": 0,
                "justificados": 0,
                "sin_registro": self.cantidad_alumnos
            }
        
        # Filtrar asistencias de la fecha
        asistencias_hoy = [a for a in self.asistencias if a.fecha == fecha]
        
        presentes = sum(1 for a in asistencias_hoy if a.estado == 'presente')
        ausentes = sum(1 for a in asistencias_hoy if a.estado == 'ausente')
        tardes = sum(1 for a in asistencias_hoy if a.estado == 'tarde')
        justificados = sum(1 for a in asistencias_hoy if a.estado == 'justificado')
        sin_registro = self.cantidad_alumnos - len(asistencias_hoy)
        
        return {
            "fecha": fecha,
            "total_alumnos": self.cantidad_alumnos,
            "presentes": presentes,
            "ausentes": ausentes,
            "tardes": tardes,
            "justificados": justificados,
            "sin_registro": sin_registro,
            "porcentaje_asistencia": round(
                (presentes / self.cantidad_alumnos * 100) if self.cantidad_alumnos > 0 else 0, 
                1
            )
        }
    
    def to_card_response(self) -> dict:
        """
        Formatea los datos del aula para mostrarlos en una tarjeta
        en el dashboard administrativo.
        """
        return {
            "id": self.id,
            "nombre_completo": self.nombre_completo,
            "nombre_corto": self.nombre_corto,
            "grado": self.grado,
            "seccion": self.seccion,
            "anio_escolar": self.anio_escolar,
            "turno": self.turno,
            "cantidad_alumnos": self.cantidad_alumnos,
            "tiene_tutor": self.tiene_tutor,
            "tiene_auxiliar": self.tiene_auxiliar,
            "es_ultimo_grado": self.es_ultimo_grado,
            "docentes_count": len(self.docentes_asignados)
        }
    
    def __repr__(self):
        return f"<Aula {self.nombre_corto} - {self.anio_escolar}>"