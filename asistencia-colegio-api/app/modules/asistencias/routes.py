from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
from app.core.database import get_db
from app.modules.asistencias.schemas import AsistenciaCreate, AsistenciaResponse
from app.modules.asistencias import services

router = APIRouter(
    prefix="/asistencias",
    tags=["Control de Asistencias / Reportes"]
)

@router.post("/", response_model=AsistenciaResponse, status_code=status.HTTP_201_CREATED)
async def tomar_asistencia(
    asistencia_in: AsistenciaCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Registra la asistencia diaria de un estudiante (Presente, Tarde, Falta)."""
    return await services.registrar_asistencia_alumno(db=db, asistencia_data=asistencia_in)

@router.get("/reporte/aula/{aula_id}", response_model=List[AsistenciaResponse])
async def obtener_reporte_diario(
    aula_id: int, 
    fecha_consulta: date, 
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el estado de asistencia de toda una sección en una fecha específica."""
    return await services.consultar_reporte_por_aula_y_fecha(
        db=db, 
        aula_id=aula_id, 
        fecha_busqueda=fecha_consulta
    )