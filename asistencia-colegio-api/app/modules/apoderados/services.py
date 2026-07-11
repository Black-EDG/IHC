from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.modules.apoderados.models import Apoderado
from app.modules.apoderados.schemas import ApoderadoCreate

async def obtener_apoderado_por_id(db: AsyncSession, apoderado_id: int):
    """Busca un apoderado por su ID único"""
    resultado = await db.execute(select(Apoderado).where(Apoderado.id == apoderado_id))
    return resultado.scalars().first()

async def obtener_apoderado_por_dni(db: AsyncSession, dni: str):
    """Busca un apoderado por su número de DNI"""
    resultado = await db.execute(select(Apoderado).where(Apoderado.dni == dni))
    return resultado.scalars().first()

async def crear_nuevo_apoderado(db: AsyncSession, apoderado_data: ApoderadoCreate):
    """Registra un apoderado validando que no esté duplicado en el sistema"""
    apoderado_existente = await obtener_apoderado_por_dni(db, apoderado_data.dni)
    if apoderado_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un apoderado registrado con este número de DNI."
        )

    nuevo_apoderado = Apoderado(**apoderado_data.model_dump())
    db.add(nuevo_apoderado)
    await db.commit()
    await db.refresh(nuevo_apoderado)
    
    return nuevo_apoderado