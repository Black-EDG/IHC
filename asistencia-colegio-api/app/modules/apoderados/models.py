from sqlalchemy import Column, Integer, String, DateTime, text
from app.core.database import Base

class Apoderado(Base):
    __tablename__ = "apoderados"

    id = Column(Integer, primary_key=True, index=True)
    
    # DATOS DEL TITULAR VINCULADO AL LOGIN
    dni = Column(String(8), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    celular = Column(String(9), nullable=False)
    parentesco = Column(String(30), nullable=False)  # Ej: 'Padre', 'Madre'
    correo = Column(String(100), nullable=True)

    # CONTACTO SECUNDARIO O DE EMERGENCIA
    contacto_emergencia_nombre = Column(String(150), nullable=True)
    contacto_emergencia_celular = Column(String(9), nullable=True)
    contacto_emergencia_parentesco = Column(String(30), nullable=True)
    
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))