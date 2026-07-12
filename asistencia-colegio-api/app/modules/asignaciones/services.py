from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.modules.asignaciones.models import AsignacionAula
from app.modules.asignaciones.schemas import AsignacionCreate

async def crear_asignacion(db: AsyncSession, asignacion_data: AsignacionCreate):
    if asignacion_data.tipo_cargo == 'docente_curso' and not asignacion_data.curso_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un docente de curso debe tener un curso asignado.")
    
    nueva_asignacion = AsignacionAula(**asignacion_data.model_dump())
    db.add(nueva_asignacion)
    await db.commit()
    await db.refresh(nueva_asignacion)
    return nueva_asignacion

async def listar_asignaciones_por_usuario(db: AsyncSession, usuario_id: int):
    resultado = await db.execute(select(AsignacionAula).where(AsignacionAula.usuario_id == usuario_id))
    return resultado.scalars().all()