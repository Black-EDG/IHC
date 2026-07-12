from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.modules.alumnos.models import Alumno
from app.modules.alumnos.schemas import AlumnoCreate, AlumnoUpdate
from app.modules.aulas.services import obtener_aula_por_id
from app.modules.apoderados.services import obtener_apoderado_por_id

async def obtener_alumno_por_id(db: AsyncSession, alumno_id: int):
    resultado = await db.execute(select(Alumno).where(Alumno.id == alumno_id))
    return resultado.scalars().first()

async def obtener_alumno_por_dni(db: AsyncSession, dni: str):
    resultado = await db.execute(select(Alumno).where(Alumno.dni == dni))
    return resultado.scalars().first()

async def listar_alumnos_por_aula(db: AsyncSession, aula_id: int):
    resultado = await db.execute(
        select(Alumno)
        .where(Alumno.aula_id == aula_id, Alumno.estado == 'matriculado')
        .order_by(Alumno.apellidos)
    )
    return resultado.scalars().all()

async def listar_hijos_por_apoderado(db: AsyncSession, apoderado_id: int):
    resultado = await db.execute(
        select(Alumno)
        .where(Alumno.apoderado_id == apoderado_id, Alumno.estado == 'matriculado')
        .order_by(Alumno.apellidos)
    )
    return resultado.scalars().all()

async def registrar_nuevo_alumno(db: AsyncSession, alumno_data: AlumnoCreate):
    alumno_existente = await obtener_alumno_por_dni(db, alumno_data.dni)
    if alumno_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de DNI ingresado ya pertenece a un estudiante registrado."
        )

    aula = await obtener_aula_por_id(db, alumno_data.aula_id)
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El aula especificada no existe en el sistema."
        )

    apoderado = await obtener_apoderado_por_id(db, alumno_data.apoderado_id)
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El apoderado especificado no se encuentra registrado."
        )

    if alumno_data.suspendido_desde and alumno_data.suspendido_hasta:
        if alumno_data.suspendido_desde > alumno_data.suspendido_hasta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio de suspensión no puede ser mayor a la fecha final."
            )

    nuevo_alumno = Alumno(**alumno_data.model_dump())
    db.add(nuevo_alumno)
    await db.commit()
    await db.refresh(nuevo_alumno)
    return nuevo_alumno

async def actualizar_alumno(db: AsyncSession, alumno_id: int, alumno_data: AlumnoUpdate):
    alumno = await obtener_alumno_por_id(db, alumno_id)
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante solicitado no existe."
        )
    
    datos_actualizados = alumno_data.model_dump(exclude_unset=True)
    
    if 'aula_id' in datos_actualizados:
        aula = await obtener_aula_por_id(db, datos_actualizados['aula_id'])
        if not aula:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El aula no existe.")
    
    if 'apoderado_id' in datos_actualizados:
        apoderado = await obtener_apoderado_por_id(db, datos_actualizados['apoderado_id'])
        if not apoderado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El apoderado no existe.")
    
    for key, value in datos_actualizados.items():
        setattr(alumno, key, value)
    
    await db.commit()
    await db.refresh(alumno)
    return alumno