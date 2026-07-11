from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.modules.alumnos.models import Alumno
from app.modules.alumnos.schemas import AlumnoCreate
from app.modules.aulas.services import obtener_aula_por_id
from app.modules.apoderados.services import obtener_apoderado_por_id

async def obtener_alumno_por_id(db: AsyncSession, alumno_id: int):
    resultado = await db.execute(select(Alumno).where(Alumno.id == alumno_id))
    return resultado.scalars().first()

async def obtener_alumno_por_dni(db: AsyncSession, dni: str):
    resultado = await db.execute(select(Alumno).where(Alumno.dni == dni))
    return resultado.scalars().first()

async def listar_alumnos_por_aula(db: AsyncSession, aula_id: int):
    """Obtiene la lista de alumnos pertenecientes a una sección específica"""
    resultado = await db.execute(select(Alumno).where(Alumno.aula_id == aula_id).order_by(Alumno.apellidos))
    return resultado.scalars().all()

async def registrar_nuevo_alumno(db: AsyncSession, alumno_data: AlumnoCreate):
    # 1. Validar duplicado de estudiante
    alumno_existente = await obtener_alumno_por_dni(db, alumno_data.dni)
    if alumno_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de DNI ingresado ya pertenece a un estudiante registrado."
        )

    # 2. Validar que el aula asignada exista en el catálogo
    aula = await obtener_aula_por_id(db, alumno_data.aula_id)
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El aula (aula_id) especificada no existe en el sistema."
        )

    # 3. Validar que el apoderado exista
    apoderado = await obtener_apoderado_por_id(db, alumno_data.apoderado_id)
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El apoderado (apoderado_id) especificado no se encuentra registrado."
        )

    # 4. Guardar cambios en la base de datos
    nuevo_alumno = Alumno(**alumno_data.model_dump())
    db.add(nuevo_alumno)
    await db.commit()
    await db.refresh(nuevo_alumno)
    
    return nuevo_alumno