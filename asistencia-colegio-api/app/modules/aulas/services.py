from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.modules.aulas.models import Aula
from app.modules.aulas.schemas import AulaCreate

async def obtener_aula_por_id(db: AsyncSession, aula_id: int):
    """Busca un aula específica por su ID único"""
    resultado = await db.execute(select(Aula).where(Aula.id == aula_id))
    return resultado.scalars().first()

async def obtener_aula_por_detalles(db: AsyncSession, grado: int, seccion: str, anio_escolar: int):
    """Busca un aula por su combinación única de grado, sección y año"""
    resultado = await db.execute(
        select(Aula).where(
            Aula.grado == grado,
            Aula.seccion == seccion,
            Aula.anio_escolar == anio_escolar
        )
    )
    return resultado.scalars().first()

async def listar_todas_las_aulas(db: AsyncSession):
    """Devuelve la lista de todos los salones registrados en el colegio"""
    resultado = await db.execute(select(Aula).order_by(Aula.grado, Aula.seccion))
    return resultado.scalars().all()

async def crear_nueva_aula(db: AsyncSession, aula_data: AulaCreate):
    """Lógica para registrar una sección nueva validando duplicados"""
    
    # 1. Validar que no exista el salón en el mismo año escolar
    aula_existente = await obtener_aula_por_detalles(
        db=db,
        grado=aula_data.grado,
        seccion=aula_data.seccion,
        anio_escolar=aula_data.anio_escolar
    )
    
    if aula_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El salón de {aula_data.grado}° '{aula_data.seccion}' ya se encuentra creado para el año {aula_data.anio_escolar}."
        )

    # 2. Mapear datos al modelo e insertar en pgAdmin
    nueva_aula = Aula(**aula_data.model_dump())
    db.add(nueva_aula)
    await db.commit()
    await db.refresh(nueva_aula)
    
    return nueva_aula