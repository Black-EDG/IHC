from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from datetime import date
from app.modules.asistencias.models import Asistencia
from app.modules.asistencias.schemas import AsistenciaCreate
from app.modules.alumnos.models import Alumno
from app.modules.alumnos.services import obtener_alumno_por_id
from app.modules.usuarios.services import obtener_usuario_por_id
from app.modules.cursos.services import obtener_curso_por_id

async def verificar_asistencia_existente(db: AsyncSession, alumno_id: int, fecha_asistencia: date, curso_id: int = None):
    query = select(Asistencia).where(
        Asistencia.alumno_id == alumno_id,
        Asistencia.fecha == fecha_asistencia,
        Asistencia.curso_id == curso_id
    )
    resultado = await db.execute(query)
    return resultado.scalars().first()

async def registrar_asistencia_alumno(db: AsyncSession, asistencia_data: AsistenciaCreate):
    fecha_final = asistencia_data.fecha or date.today()

    alumno = await obtener_alumno_por_id(db, asistencia_data.alumno_id)
    if not alumno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El alumno especificado no existe.")

    usuario = await obtener_usuario_por_id(db, asistencia_data.usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario que registra no existe.")

    if asistencia_data.curso_id:
        curso = await obtener_curso_por_id(db, asistencia_data.curso_id)
        if not curso:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El curso especificado no existe.")

    ya_registrado = await verificar_asistencia_existente(db, asistencia_data.alumno_id, fecha_final, asistencia_data.curso_id)
    if ya_registrado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya se registró la asistencia de este alumno para la fecha {fecha_final}."
        )

    datos_asistencia = asistencia_data.model_dump()
    datos_asistencia["fecha"] = fecha_final
    
    nueva_asistencia = Asistencia(**datos_asistencia)
    db.add(nueva_asistencia)
    await db.commit()
    await db.refresh(nueva_asistencia)
    return nueva_asistencia

async def consultar_reporte_por_aula_y_fecha(db: AsyncSession, aula_id: int, fecha_busqueda: date, curso_id: int = None):
    query = select(Asistencia).join(Alumno, Asistencia.alumno_id == Alumno.id).where(
        Alumno.aula_id == aula_id,
        Asistencia.fecha == fecha_busqueda
    )
    if curso_id:
        query = query.where(Asistencia.curso_id == curso_id)
    
    resultado = await db.execute(query)
    return resultado.scalars().all()