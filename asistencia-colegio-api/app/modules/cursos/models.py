from sqlalchemy import Column, Integer, String, DateTime, Text, text
from app.core.database import Base

class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    creado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))