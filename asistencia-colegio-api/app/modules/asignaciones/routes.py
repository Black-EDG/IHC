from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.modules.asignaciones import services
from app.modules.asignaciones.schemas import (
    AsignacionCreate,
    AsignacionUpdate,
    AsignacionMasivaRequest,
)

router = APIRouter(
    prefix="/asignaciones",
    tags=["🔗 Asignaciones / Docentes-Aulas"]
)

# ═══════════════════════════════════════════════════════════════
# CRUD BÁSICO
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva asignación"
)
async def crear_asignacion(
    data: AsignacionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Asigna un usuario a un aula con un rol específico."""
    return await services.crear_asignacion(db=db, data=data)


@router.post(
    "/masiva",
    status_code=status.HTTP_201_CREATED,
    summary="Asignación masiva de docente a múltiples aulas"
)
async def crear_asignacion_masiva(
    data: AsignacionMasivaRequest,
    db: AsyncSession = Depends(get_db)
):
    """Asigna un docente a múltiples aulas para un mismo curso."""
    return await services.crear_asignacion_masiva(db=db, data=data)


@router.get(
    "/",
    summary="Listar todas las asignaciones"
)
async def listar_asignaciones(
    anio_escolar: Optional[int] = Query(None),
    tipo_cargo: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Lista todas las asignaciones con filtros opcionales."""
    return await services.obtener_todas_las_asignaciones(
        db=db, skip=skip, limit=limit, anio_escolar=anio_escolar, tipo_cargo=tipo_cargo
    )


@router.get(
    "/dashboard/{usuario_id}",
    summary="Dashboard del docente al iniciar sesión"
)
async def dashboard_docente(
    usuario_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint principal cuando un docente inicia sesión."""
    return await services.obtener_dashboard_docente(db=db, usuario_id=usuario_id)


@router.get(
    "/usuario/{usuario_id}",
    summary="Asignaciones de un usuario"
)
async def asignaciones_por_usuario(
    usuario_id: int,
    tipo_cargo: Optional[str] = Query(None),
    anio_escolar: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todas las asignaciones de un usuario específico."""
    asignaciones = await services.obtener_asignaciones_por_usuario(
        db=db, usuario_id=usuario_id, tipo_cargo=tipo_cargo, anio_escolar=anio_escolar
    )
    if not asignaciones:
        raise HTTPException(status_code=404, detail="El usuario no tiene asignaciones.")
    return asignaciones


@router.get(
    "/aula/{aula_id}",
    summary="Resumen de asignaciones de un aula"
)
async def resumen_aula(
    aula_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el resumen completo de asignaciones de un aula."""
    return await services.obtener_resumen_aula(db=db, aula_id=aula_id)


@router.get(
    "/{asignacion_id}",
    summary="Ver asignación por ID"
)
async def ver_asignacion(
    asignacion_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el detalle completo de una asignación por su ID."""
    asignacion = await services.obtener_asignacion_por_id(db, asignacion_id)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada.")
    return asignacion


@router.patch(
    "/{asignacion_id}",
    summary="Actualizar asignación"
)
async def actualizar_asignacion(
    asignacion_id: int,
    data: AsignacionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza los datos de una asignación existente."""
    resultado = await services.actualizar_asignacion(db, asignacion_id, data)
    if not resultado:
        raise HTTPException(status_code=404, detail="Asignación no encontrada.")
    return resultado


@router.delete(
    "/{asignacion_id}",
    summary="Eliminar asignación"
)
async def eliminar_asignacion(
    asignacion_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Elimina permanentemente una asignación del sistema."""
    resultado = await services.eliminar_asignacion(db, asignacion_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Asignación no encontrada.")
    return {"mensaje": "Asignación eliminada correctamente.", "status": "success"}