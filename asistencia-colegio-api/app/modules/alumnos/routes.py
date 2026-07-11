from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.modules.alumnos.schemas import AlumnoCreate, AlumnoResponse
from app.modules.alumnos import services

router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnado / Estudiantes"]
)

@router.post("/", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
async def matricular_alumno(
    alumno_in: AlumnoCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Registra y matricula a un nuevo alumno vinculando su aula y apoderado."""
    return await services.registrar_nuevo_alumno(db=db, alumno_data=alumno_in)

@router.get("/aula/{aula_id}", response_model=List[AlumnoResponse])
async def obtener_alumnos_aula(aula_id: int, db: AsyncSession = Depends(get_db)):
    """Lista a todos los alumnos matriculados en un aula específica."""
    return await services.listar_alumnos_por_aula(db=db, aula_id=aula_id)

@router.get("/{alumno_id}", response_model=AlumnoResponse)
async def obtener_alumno(alumno_id: int, db: AsyncSession = Depends(get_db)):
    """Busca la ficha escolar de un estudiante por su ID único."""
    alumno = await services.obtener_alumno_por_id(db=db, alumno_id=alumno_id)
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante solicitado no figura en las listas de matrícula."
        )
    return alumno