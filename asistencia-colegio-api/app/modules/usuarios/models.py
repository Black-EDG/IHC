import enum
from sqlalchemy import Column, Integer, String, DateTime, text
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
    dni = Column(String(8), unique=True, nullable=False)
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
        server_default=text("'activo'")
    )
    
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))