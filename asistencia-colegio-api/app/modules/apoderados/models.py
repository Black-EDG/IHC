import enum
from sqlalchemy import Column, Integer, String, DateTime, text, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Parentesco(str, enum.Enum):
    """Tipos de parentesco normalizados para el sistema escolar peruano"""
    PADRE = 'Padre'
    MADRE = 'Madre'
    TIO = 'Tío'
    TIA = 'Tía'
    HERMANO_MAYOR = 'Hermano Mayor'
    HERMANA_MAYOR = 'Hermana Mayor'
    ABUELO = 'Abuelo'
    ABUELA = 'Abuela'
    TUTOR_LEGAL = 'Tutor Legal'
    MADRINA = 'Madrina'
    PADRINO = 'Padrino'
    OTRO = 'Otro'

class Apoderado(Base):
    __tablename__ = "apoderados"

    id = Column(Integer, primary_key=True, index=True)
    
    # DATOS DEL APODERADO TITULAR (El que se loguea con su DNI)
    dni = Column(String(8), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    celular = Column(String(9), nullable=False)
    parentesco = Column(String(30), nullable=False)
    correo = Column(String(100), nullable=True)
    
    # CONTACTO DE EMERGENCIA (Se usa si el titular no responde a las alertas)
    contacto_emergencia_nombre = Column(String(150), nullable=True)
    contacto_emergencia_celular = Column(String(9), nullable=True)
    contacto_emergencia_parentesco = Column(String(30), nullable=True)
    
    # CONTROL DE VERIFICACIÓN DE CELULAR (Para futuros SMS)
    celular_verificado = Column(
        String(1), 
        server_default=text("'N'"),
        nullable=False
    )
    
    # FECHA DE CREACIÓN DEL REGISTRO
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    
    # CONSTRAINTS DE VALIDACIÓN
    __table_args__ = (
        CheckConstraint(
            "celular ~ '^[0-9]{9}$'",
            name="check_celular_formato_valido"
        ),
        CheckConstraint(
            "contacto_emergencia_celular IS NULL OR contacto_emergencia_celular ~ '^[0-9]{9}$'",
            name="check_celular_emergencia_formato_valido"
        ),
        CheckConstraint(
            "correo IS NULL OR correo ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name="check_correo_formato_valido"
        ),
        CheckConstraint(
            "celular_verificado IN ('S', 'N')",
            name="check_celular_verificado_valor"
        ),
    )
    
    # RELACIONES
    alumnos = relationship(
        "Alumno", 
        back_populates="apoderado", 
        lazy="selectin",
        foreign_keys="Alumno.apoderado_id"
    )
    
    alertas = relationship(
        "Alerta", 
        back_populates="apoderado", 
        lazy="selectin",
        foreign_keys="Alerta.apoderado_id"
    )
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del apoderado"""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def tiene_contacto_emergencia(self) -> bool:
        """Verifica si tiene configurado un contacto de emergencia"""
        return bool(self.contacto_emergencia_nombre and self.contacto_emergencia_celular)
    
    @property
    def cantidad_hijos(self) -> int:
        """Retorna la cantidad de hijos vinculados a este apoderado"""
        return len(self.alumnos) if self.alumnos else 0
    
    @property
    def celular_esta_verificado(self) -> bool:
        """Verifica si el celular ya fue verificado para envío de SMS"""
        return self.celular_verificado == 'S'
    
    def obtener_hijos_activos(self) -> list:
        """Retorna solo los hijos que están matriculados actualmente"""
        from app.modules.alumnos.models import EstadoAlumno
        if not self.alumnos:
            return []
        return [alumno for alumno in self.alumnos if alumno.estado == EstadoAlumno.matriculado]
    
    def to_bandeja_hijos(self) -> list:
        """
        Formatea la lista de hijos para la bandeja de selección en la app del padre
        Retorna: [{"id": 1, "nombre_completo": "Yhury Anampa", "grado_seccion": "1° A"}]
        """
        hijos_activos = self.obtener_hijos_activos()
        return [
            {
                "id": hijo.id,
                "nombre_completo": hijo.nombre_completo,
                "dni": hijo.dni,
                "grado": f"{hijo.aula.grado}°" if hijo.aula else "Sin asignar",
                "seccion": hijo.aula.seccion if hijo.aula else "",
                "grado_seccion": f"{hijo.aula.grado}° {hijo.aula.seccion}" if hijo.aula else "Sin aula",
                "estado": hijo.estado.value if hijo.estado else "desconocido"
            }
            for hijo in hijos_activos
        ]
    
    def __repr__(self):
        return f"<Apoderado {self.dni} - {self.nombre_completo} ({self.cantidad_hijos} hijos)>"