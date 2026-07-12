from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.modules.cursos.models import Curso
from app.modules.cursos.schemas import CursoCreate

async def obtener_curso_por_id(db: AsyncSession, curso_id: int):
    resultado = await db.execute(select(Curso).where(Curso.id == curso_id))
    return resultado.scalars().first()

async def listar_todos_los_cursos(db: AsyncSession):
    resultado = await db.execute(select(Curso).order_by(Curso.nombre))
    return resultado.scalars().all()

async def crear_nuevo_curso(db: AsyncSession, curso_data: CursoCreate):
    resultado = await db.execute(select(Curso).where(Curso.nombre == curso_data.nombre))
    if resultado.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El curso ya existe.")
    
    nuevo_curso = Curso(**curso_data.model_dump())
    db.add(nuevo_curso)
    await db.commit()
    await db.refresh(nuevo_curso)
    return nuevo_curso