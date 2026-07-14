import enum
from sqlalchemy import Column, Integer, String, DateTime, text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.core.database import Base

class RolUsuario(str, enum.Enum):
    admin = 'admin'
    auxiliar = 'auxiliar'
    docente = 'docente'

class EstadoUsuario(str, enum.Enum):
    activo = 'activo'
    licencia = 'licencia'
    inactivo = 'inactivo'

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(8), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    celular = Column(String(9), nullable=True)
    correo = Column(String(100), unique=True, nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    
    rol = Column(
        PG_ENUM(RolUsuario, name="rol_usuario", create_type=False), 
        nullable=False
    )
    estado = Column(
        PG_ENUM(EstadoUsuario, name="estado_usuario", create_type=False), 
        server_default=text("'activo'"),
        nullable=False
    )
    
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # Relaciones con nombres explícitos y lazy loading optimizado
    asignaciones = relationship(
        "AsignacionAula", 
        back_populates="usuario", 
        lazy="selectin",
        foreign_keys="AsignacionAula.usuario_id"
    )
    asistencias_registradas = relationship(
        "Asistencia", 
        back_populates="usuario", 
        lazy="selectin",
        foreign_keys="Asistencia.usuario_id"
    )

    @property
    def nombre_completo(self) -> str:
        """Propiedad calculada para obtener el nombre completo"""
        return f"{self.nombres} {self.apellidos}"

    @property
    def is_admin(self) -> bool:
        return self.rol == RolUsuario.admin

    @property
    def is_docente(self) -> bool:
        return self.rol == RolUsuario.docente

    @property
    def is_auxiliar(self) -> bool:
        return self.rol == RolUsuario.auxiliar

    def __repr__(self):
        return f"<Usuario {self.dni} - {self.nombre_completo} ({self.rol.value})>"