from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.modules.cursos.schemas import CursoCreate, CursoResponse
from app.modules.cursos import services

router = APIRouter(prefix="/cursos", tags=["Plan de Estudios / Cursos"])

@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_curso(curso_in: CursoCreate, db: AsyncSession = Depends(get_db)):
    return await services.crear_nuevo_curso(db=db, curso_data=curso_in)

@router.get("/", response_model=List[CursoResponse])
async def listar_cursos(db: AsyncSession = Depends(get_db)):
    return await services.listar_todos_los_cursos(db=db)

@router.get("/{curso_id}", response_model=CursoResponse)
async def obtener_curso(curso_id: int, db: AsyncSession = Depends(get_db)):
    curso = await services.obtener_curso_por_id(db=db, curso_id=curso_id)
    if not curso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado.")
    return curso