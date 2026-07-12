from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.modules.alumnos.schemas import AlumnoCreate, AlumnoUpdate, AlumnoResponse
from app.modules.alumnos import services

router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnado / Estudiantes"]
)

@router.post("/", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
async def matricular_alumno(alumno_in: AlumnoCreate, db: AsyncSession = Depends(get_db)):
    return await services.registrar_nuevo_alumno(db=db, alumno_data=alumno_in)

@router.get("/aula/{aula_id}", response_model=List[AlumnoResponse])
async def obtener_alumnos_aula(aula_id: int, db: AsyncSession = Depends(get_db)):
    return await services.listar_alumnos_por_aula(db=db, aula_id=aula_id)

@router.get("/apoderado/{apoderado_id}", response_model=List[AlumnoResponse])
async def obtener_hijos_apoderado(apoderado_id: int, db: AsyncSession = Depends(get_db)):
    return await services.listar_hijos_por_apoderado(db=db, apoderado_id=apoderado_id)

@router.get("/{alumno_id}", response_model=AlumnoResponse)
async def obtener_alumno(alumno_id: int, db: AsyncSession = Depends(get_db)):
    alumno = await services.obtener_alumno_por_id(db=db, alumno_id=alumno_id)
    if not alumno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alumno no encontrado.")
    return alumno

@router.patch("/{alumno_id}", response_model=AlumnoResponse)
async def editar_alumno(alumno_id: int, alumno_in: AlumnoUpdate, db: AsyncSession = Depends(get_db)):
    return await services.actualizar_alumno(db=db, alumno_id=alumno_id, alumno_data=alumno_in)