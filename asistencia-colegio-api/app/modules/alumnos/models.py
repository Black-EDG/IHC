from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, text
from app.core.database import Base

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(8), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    
    # Llaves foráneas vinculadas a infraestructura y entorno familiar
    aula_id = Column(Integer, ForeignKey("aulas.id", ondelete="RESTRICT"), nullable=False)
    apoderado_id = Column(Integer, ForeignKey("apoderados.id", ondelete="RESTRICT"), nullable=False)
    
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))