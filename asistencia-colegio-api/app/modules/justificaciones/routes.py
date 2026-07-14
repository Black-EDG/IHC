from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.modules.justificaciones import services
from app.modules.justificaciones.schemas import (
    JustificacionCreate,
    JustificacionUpdateAuxiliar,
    JustificacionResponse,
    JustificacionCardResponse,
    VerificarJustificacionesVirtualesResponse,
    EstadisticasJustificacionesResponse
)

router = APIRouter(
    prefix="/justificaciones",
    tags=["📝 Justificaciones"]
)

# ═══════════════════════════════════════════════════════════════
# FLUJO DEL PADRE (APP FAMILIAR)
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/verificar/{alumno_id}",
    response_model=VerificarJustificacionesVirtualesResponse,
    summary="Verificar si puede justificar virtualmente"
)
async def verificar_justificaciones_disponibles(
    alumno_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Endpoint para la App Familiar.**
    
    Antes de mostrar el botón "Justificar Inasistencia", 
    la app consulta este endpoint para saber:
    
    - Cuántas faltas consecutivas tiene el alumno
    - Cuántas justificaciones virtuales ha usado
    - Si aún puede justificar virtualmente
    
    **Regla:** Máximo 3 justificaciones virtuales consecutivas.
    A la 4ta falta, debe ir presencialmente al colegio.
    """
    return await services.verificar_justificaciones_virtuales_disponibles(db, alumno_id)


@router.post(
    "/",
    response_model=JustificacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar justificación (Padre de Familia)"
)
async def crear_justificacion(
    data: JustificacionCreate,
    alumno_id: int = Query(..., description="ID del alumno (hijo del padre logueado)"),
    db: AsyncSession = Depends(get_db)
):
    """
    **Endpoint de la App Familiar para justificar una inasistencia.**
    
    El padre:
    1. Selecciona a su hijo
    2. Ve la lista de faltas
    3. Elige una falta para justificar
    4. Escribe el motivo
    5. Opcionalmente sube una foto del certificado médico
    
    **Validaciones:**
    - Solo puede justificar faltas de sus hijos
    - Máximo 3 justificaciones virtuales consecutivas
    - No puede justificar una falta ya justificada
    """
    return await services.crear_justificacion(db, data, alumno_id)


@router.get(
    "/alumno/{alumno_id}",
    response_model=List[JustificacionCardResponse],
    summary="Historial de justificaciones de un alumno"
)
async def justificaciones_por_alumno(
    alumno_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Historial de justificaciones de un alumno.**
    
    Usado por:
    - El padre para ver el estado de sus justificaciones
    - El tutor para revisar el historial del alumno
    """
    justificaciones = await services.obtener_justificaciones_por_alumno(db, alumno_id)
    if not justificaciones:
        return []
    return justificaciones


# ═══════════════════════════════════════════════════════════════
# FLUJO DEL AUXILIAR (REVISIÓN)
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/pendientes",
    response_model=List[JustificacionCardResponse],
    summary="Justificaciones pendientes de revisión"
)
async def justificaciones_pendientes(
    db: AsyncSession = Depends(get_db)
):
    """
    **Lista de justificaciones pendientes que el Auxiliar debe revisar.**
    
    El Auxiliar revisa cada justificación y decide si:
    - **Aprueba**: La falta se convierte en 'justificado'
    - **Rechaza**: La falta sigue como 'ausente' (debe explicar por qué)
    """
    return await services.obtener_justificaciones_pendientes(db)


@router.get(
    "/",
    response_model=List[JustificacionCardResponse],
    summary="Listar todas las justificaciones"
)
async def listar_justificaciones(
    estado: Optional[str] = Query(None, description="Filtrar: pendiente, aprobada, rechazada"),
    alumno_id: Optional[int] = Query(None, description="Filtrar por alumno"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Lista todas las justificaciones con filtros."""
    return await services.obtener_todas_las_justificaciones(
        db=db, skip=skip, limit=limit, estado=estado, alumno_id=alumno_id
    )


@router.get(
    "/{justificacion_id}",
    response_model=JustificacionResponse,
    summary="Ver justificación por ID"
)
async def ver_justificacion(
    justificacion_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el detalle completo de una justificación."""
    justificacion = await services.obtener_justificacion_por_id(db, justificacion_id)
    if not justificacion:
        raise HTTPException(status_code=404, detail="Justificación no encontrada.")
    return justificacion


@router.patch(
    "/{justificacion_id}/revisar",
    response_model=JustificacionResponse,
    summary="Aprobar o Rechazar justificación (Auxiliar)"
)
async def revisar_justificacion(
    justificacion_id: int,
    data: JustificacionUpdateAuxiliar,
    auxiliar_id: int = Query(..., description="ID del Auxiliar que revisa"),
    db: AsyncSession = Depends(get_db)
):
    """
    **El Auxiliar aprueba o rechaza una justificación.**
    
    - **APROBAR**: La falta se marca como 'justificado'. 
      El alumno recupera la asistencia.
    - **RECHAZAR**: La falta sigue como 'ausente'. 
      Debe explicar el motivo del rechazo.
    """
    return await services.aprobar_justificacion(db, justificacion_id, data, auxiliar_id)


# ═══════════════════════════════════════════════════════════════
# ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/estadisticas/generales",
    response_model=EstadisticasJustificacionesResponse,
    summary="Estadísticas generales de justificaciones"
)
async def estadisticas_justificaciones(
    db: AsyncSession = Depends(get_db)
):
    """Estadísticas generales para el dashboard administrativo."""
    return await services.obtener_estadisticas_justificaciones(db)