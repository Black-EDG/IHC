from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from datetime import date
from app.modules.asistencias.models import Asistencia
from app.modules.asistencias.schemas import AsistenciaCreate
from app.modules.alumnos.services import obtener_alumno_por_id
from app.modules.usuarios.services import obtener_usuario_por_id

async def verificar_asistencia_existente(db: AsyncSession, alumno_id: int, fecha_asistencia: date):
    """Verifica si ya existe un registro para el alumno en esa fecha"""
    resultado = await db.execute(
        select(Asistencia).where(
            Asistencia.alumno_id == alumno_id,
            Asistencia.fecha == fecha_asistencia
        )
    )
    return resultado.scalars().first()

async def registrar_asistencia_alumno(db: AsyncSession, asistencia_data: AsistenciaCreate):
    # 1. Si no mandan fecha, asignamos la fecha de hoy por defecto
    fecha_final = asistencia_data.fecha or date.today()

    # 2. Validar que el alumno exista en el plantel
    alumno = await obtener_alumno_por_id(db, asistencia_data.alumno_id)
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El alumno especificado no existe."
        )

    # 3. Validar que el usuario que registra exista
    usuario = await obtener_usuario_por_id(db, asistencia_data.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario (profesor/auxiliar) que intenta registrar no existe."
        )

    # 4. Validar duplicados para el mismo día
    ya_registrado = await verificar_asistencia_existente(db, asistencia_data.alumno_id, fecha_final)
    if ya_registrado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya se registró la asistencia de este alumno para la fecha {fecha_final}."
        )

    # 5. Guardar en PostgreSQL de forma asíncrona
    datos_asistencia = asistencia_data.model_dump()
    datos_asistencia["fecha"] = fecha_final # Sobrescribimos con la fecha calculada
    
    nueva_asistencia = Asistencia(**datos_asistencia)
    db.add(nueva_asistencia)
    await db.commit()
    await db.refresh(nueva_asistencia)
    
    return nueva_asistencia

async def consultar_reporte_por_aula_y_fecha(db: AsyncSession, aula_id: int, fecha_busqueda: date):
    """Devuelve las asistencias de un salón en una fecha específica (Útil para reportes)"""
    from app.modules.alumnos.models import Alumno
    
    # Hacemos un JOIN asíncrono entre Asistencias y Alumnos filtrando por aula
    resultado = await db.execute(
        select(Asistencia)
        .join(Alumno, Asistencia.alumno_id == Alumno.id)
        .where(Alumno.aula_id == aula_id, Asistencia.fecha == fecha_busqueda)
    )
    return resultado.scalars().all()