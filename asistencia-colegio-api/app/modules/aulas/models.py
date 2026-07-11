from sqlalchemy import Column, Integer, SmallInteger, String, CheckConstraint, UniqueConstraint
from app.core.database import Base

class Aula(Base):
    __tablename__ = "aulas"

    id = Column(Integer, primary_key=True, index=True)
    grado = Column(SmallInteger, nullable=False)
    seccion = Column(String(2), nullable=False)  # 'A', 'B', 'C', etc.
    anio_escolar = Column(Integer, nullable=False)  # Ej: 2026
    turno = Column(String(10), server_default="mañana")

    # Mapeamos las restricciones exactamente igual a como están en tu base de datos
    __table_args__ = (
        CheckConstraint('grado >= 1 AND grado <= 5', name='check_grado_secundaria'),
        UniqueConstraint('grado', 'seccion', 'anio_escolar', name='unica_seccion_por_anio'),
    )