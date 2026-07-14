from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.modules.asignaciones import services
from app.modules.asignaciones.schemas import (
    AsignacionCreate,
    AsignacionResponse,
    AsignacionUpdate,
    AsignacionCardResponse,
    AsignacionMasivaRequest,
    DashboardDocenteResponse,
    ResumenAulaResponse
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
    response_model=AsignacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva asignación"
)
async def crear_asignacion(
    data: AsignacionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Asigna un usuario a un aula con un rol específico (docente_curso, tutor_seccion, auxiliar_grado)."""
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
    """Asigna un docente a múltiples aulas para un mismo curso de una sola vez."""
    return await services.crear_asignacion_masiva(db=db, data=data)


@router.get(
    "/",
    response_model=List[AsignacionCardResponse],
    summary="Listar todas las asignaciones"
)
async def listar_asignaciones(
    anio_escolar: Optional[int] = Query(None, description="Filtrar por año escolar"),
    tipo_cargo: Optional[str] = Query(None, description="Filtrar por tipo: docente_curso, tutor_seccion, auxiliar_grado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Lista todas las asignaciones con filtros opcionales por año escolar y tipo de cargo."""
    return await services.obtener_todas_las_asignaciones(
        db=db, skip=skip, limit=limit, anio_escolar=anio_escolar, tipo_cargo=tipo_cargo
    )


@router.get(
    "/{asignacion_id}",
    response_model=AsignacionResponse,
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
    response_model=AsignacionResponse,
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


# ═══════════════════════════════════════════════════════════════
# DASHBOARD Y REPORTES
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/dashboard/{usuario_id}",
    response_model=DashboardDocenteResponse,
    summary="Dashboard del docente al iniciar sesión"
)
async def dashboard_docente(
    usuario_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Endpoint principal cuando un docente/tutor/auxiliar inicia sesión.**
    
    Retorna todas sus asignaciones organizadas por tipo:
    - **asignaciones_docente**: Cursos que dicta y en qué aulas
    - **asignaciones_tutor**: Secciones donde es tutor
    - **asignaciones_auxiliar**: Grados donde es auxiliar
    
    Con esta información, el frontend muestra solo las aulas
    y cursos que le corresponden al profesor.
    """
    return await services.obtener_dashboard_docente(db=db, usuario_id=usuario_id)


@router.get(
    "/usuario/{usuario_id}",
    response_model=List[AsignacionCardResponse],
    summary="Asignaciones de un usuario"
)
async def asignaciones_por_usuario(
    usuario_id: int,
    tipo_cargo: Optional[str] = Query(None, description="Filtrar por tipo: docente_curso, tutor_seccion, auxiliar_grado"),
    anio_escolar: Optional[int] = Query(None, description="Filtrar por año escolar"),
    db: AsyncSession = Depends(get_db)
):
    """
    **Obtiene todas las asignaciones de un usuario específico.**
    
    Útil para:
    - Ver todos los cursos que dicta un docente
    - Ver todas las secciones donde es tutor
    - Ver todos los grados donde es auxiliar
    """
    asignaciones = await services.obtener_asignaciones_por_usuario(
        db=db, usuario_id=usuario_id, tipo_cargo=tipo_cargo, anio_escolar=anio_escolar
    )
    if not asignaciones:
        raise HTTPException(
            status_code=404, 
            detail="El usuario no tiene asignaciones con los filtros especificados."
        )
    return asignaciones


@router.get(
    "/aula/{aula_id}",
    response_model=ResumenAulaResponse,
    summary="Resumen de asignaciones de un aula"
)
async def resumen_aula(
    aula_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Obtiene el resumen completo de asignaciones de un aula.**
    
    Muestra:
    - Todos los docentes con sus respectivos cursos
    - Tutor asignado (si tiene)
    - Auxiliar asignado (si tiene)
    
    Útil para ver la plana docente completa de un salón.
    """
    return await services.obtener_resumen_aula(db=db, aula_id=aula_id)