import enum
from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, 
    text, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class EstadoAlumno(str, enum.Enum):
    """Estados oficiales del alumno en el sistema escolar peruano"""
    MATRICULADO = 'matriculado'
    TRASLADADO = 'trasladado'
    RETIRADO = 'retirado'

class GeneroAlumno(str, enum.Enum):
    """Género del alumno para reportes estadísticos"""
    MASCULINO = 'M'
    FEMENINO = 'F'

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    
    # DATOS PERSONALES
    dni = Column(String(8), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    genero = Column(
        PG_ENUM(GeneroAlumno, name="genero_alumno_enum", create_type=False),
        nullable=False
    )
    fecha_nacimiento = Column(Date, nullable=False)
    
    # CONEXIONES FUNDAMENTALES
    aula_id = Column(
        Integer, 
        ForeignKey('aulas.id', ondelete='RESTRICT'), 
        nullable=False,
        index=True
    )
    apoderado_id = Column(
        Integer, 
        ForeignKey('apoderados.id', ondelete='RESTRICT'), 
        nullable=False,
        index=True
    )
    
    # ESTADO OFICIAL
    estado = Column(
        PG_ENUM(EstadoAlumno, name="estado_alumno", create_type=False),
        server_default=text("'matriculado'"),
        nullable=False
    )
    
    # CONTROL DE SUSPENSIONES
    suspendido_desde = Column(Date, nullable=True)
    suspendido_hasta = Column(Date, nullable=True)
    
    # FECHA DE CREACIÓN DEL REGISTRO
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    
    # CONSTRAINTS
    __table_args__ = (
        CheckConstraint(
            "dni ~ '^[0-9]{8}$'",
            name="check_alumno_dni_formato"
        ),
        CheckConstraint(
            "fecha_nacimiento <= CURRENT_DATE - INTERVAL '10 years'",
            name="check_edad_minima_secundaria"
        ),
        CheckConstraint(
            "fecha_nacimiento <= CURRENT_DATE - INTERVAL '11 years' OR "
            "fecha_nacimiento IS NOT NULL",
            name="check_edad_coherente"
        ),
        CheckConstraint(
            "suspendido_desde IS NULL AND suspendido_hasta IS NULL OR "
            "(suspendido_desde IS NOT NULL AND suspendido_hasta IS NOT NULL)",
            name="check_suspension_ambos_campos"
        ),
        CheckConstraint(
            "suspendido_desde <= suspendido_hasta",
            name="check_fechas_suspension"
        ),
        Index("idx_alumnos_aula", "aula_id"),
        Index("idx_alumnos_apoderado", "apoderado_id"),
        Index("idx_alumnos_estado", "estado"),
    )
    
    # RELACIONES
    aula = relationship(
        "Aula", 
        back_populates="alumnos", 
        lazy="selectin",
        foreign_keys=[aula_id]
    )
    apoderado = relationship(
        "Apoderado", 
        back_populates="alumnos", 
        lazy="selectin",
        foreign_keys=[apoderado_id]
    )
    asistencias = relationship(
        "Asistencia", 
        back_populates="alumno", 
        lazy="selectin",
        foreign_keys="Asistencia.alumno_id"
    )
    alertas = relationship(
        "Alerta", 
        back_populates="alumno", 
        lazy="selectin",
        foreign_keys="Alerta.alumno_id"
    )
    
    # ═══════════════════════════════════════════════════════════
    # PROPIEDADES CALCULADAS
    # ═══════════════════════════════════════════════════════════
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del alumno"""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def edad(self) -> int:
        """Calcula la edad actual del alumno"""
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        # Ajustar si aún no cumple años este año
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad
    
    @property
    def grado_seccion(self) -> str:
        """Retorna el grado y sección formateado: '1° A'"""
        if self.aula:
            return f"{self.aula.grado}° {self.aula.seccion}"
        return "Sin aula asignada"
    
    @property
    def esta_matriculado(self) -> bool:
        """Verifica si el alumno está activo"""
        return self.estado == EstadoAlumno.MATRICULADO
    
    @property
    def esta_suspendido(self) -> bool:
        """Verifica si el alumno está actualmente suspendido"""
        if not self.suspendido_desde or not self.suspendido_hasta:
            return False
        hoy = date.today()
        return self.suspendido_desde <= hoy <= self.suspendido_hasta
    
    @property
    def dias_suspension_restantes(self) -> int:
        """Calcula cuántos días le quedan de suspensión"""
        if not self.esta_suspendido:
            return 0
        hoy = date.today()
        delta = self.suspendido_hasta - hoy
        return max(0, delta.days)
    
    @property
    def puede_ser_promovido(self) -> bool:
        """
        Verifica si el alumno puede ser promovido al siguiente grado.
        No puede estar en 5° (último año) ni estar retirado/trasladado.
        """
        if not self.esta_matriculado:
            return False
        if self.aula and self.aula.grado >= 5:
            return False
        return True
    
    # ═══════════════════════════════════════════════════════════
    # MÉTODOS DE NEGOCIO
    # ═══════════════════════════════════════════════════════════
    
    def suspender(self, desde: date, hasta: date) -> None:
        """
        Suspende al alumno por un período específico.
        Lanza ValueError si las fechas son inválidas.
        """
        if desde > hasta:
            raise ValueError("La fecha de inicio de suspensión no puede ser mayor a la de fin.")
        if desde < date.today():
            raise ValueError("No se puede suspender con fecha pasada.")
        
        self.suspendido_desde = desde
        self.suspendido_hasta = hasta
    
    def levantar_suspension(self) -> None:
        """Elimina la suspensión activa del alumno"""
        self.suspendido_desde = None
        self.suspendido_hasta = None
    
    def trasladar(self, nueva_aula_id: int) -> None:
        """
        Traslada al alumno a otra aula.
        No cambia el estado del alumno, solo el aula.
        """
        self.aula_id = nueva_aula_id
    
    def retirar(self) -> None:
        """Marca al alumno como retirado del colegio"""
        self.estado = EstadoAlumno.RETIRADO
        self.levantar_suspension()
    
    def resumen_asistencias(self, fecha_inicio: date = None, fecha_fin: date = None) -> dict:
        """
        Calcula un resumen de asistencias del alumno en un período.
        Si no se especifican fechas, toma el año escolar actual.
        """
        if not self.asistencias:
            return {"total": 0, "presentes": 0, "ausentes": 0, "tardes": 0, "justificados": 0}
        
        # Filtrar por fechas si se proporcionan
        asistencias_filtradas = self.asistencias
        if fecha_inicio:
            asistencias_filtradas = [a for a in asistencias_filtradas if a.fecha >= fecha_inicio]
        if fecha_fin:
            asistencias_filtradas = [a for a in asistencias_filtradas if a.fecha <= fecha_fin]
        
        total = len(asistencias_filtradas)
        presentes = sum(1 for a in asistencias_filtradas if a.estado == 'presente')
        ausentes = sum(1 for a in asistencias_filtradas if a.estado == 'ausente')
        tardes = sum(1 for a in asistencias_filtradas if a.estado == 'tarde')
        justificados = sum(1 for a in asistencias_filtradas if a.estado == 'justificado')
        
        return {
            "total": total,
            "presentes": presentes,
            "ausentes": ausentes,
            "tardes": tardes,
            "justificados": justificados,
            "porcentaje_asistencia": round((presentes / total * 100) if total > 0 else 0, 1),
            "riesgo_inhabilitacion": ausentes > (total * 0.3) if total > 0 else False
        }
    
    def to_card_response(self) -> dict:
        """
        Formatea los datos del alumno para mostrarlos en una tarjeta
        en la app del padre o en el dashboard administrativo.
        """
        return {
            "id": self.id,
            "dni": self.dni,
            "nombre_completo": self.nombre_completo,
            "genero": self.genero.value if self.genero else None,
            "edad": self.edad,
            "grado_seccion": self.grado_seccion,
            "estado": self.estado.value if self.estado else "desconocido",
            "suspendido": self.esta_suspendido,
            "dias_suspension_restantes": self.dias_suspension_restantes,
            "apoderado_nombre": self.apoderado.nombre_completo if self.apoderado else "Sin apoderado",
            "apoderado_celular": self.apoderado.celular if self.apoderado else None,
        }
    
    def __repr__(self):
        return f"<Alumno {self.dni} - {self.nombre_completo} ({self.grado_seccion})>"