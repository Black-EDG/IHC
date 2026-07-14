from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.modules.alertas import services
from app.modules.alertas.schemas import (
    AlertaResponse,
    AlertaCardResponse,
    DispararAlertasResponse,
    EstadisticasAlertasResponse
)

router = APIRouter(
    prefix="/alertas",
    tags=["🔔 Alertas / SMS y Citaciones"]
)

# ═══════════════════════════════════════════════════════════════
# PROCESO AUTOMÁTICO (SCHEDULER)
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/disparar",
    response_model=DispararAlertasResponse,
    summary="🚀 Ejecutar proceso automático de alertas"
)
async def disparar_alertas(
    db: AsyncSession = Depends(get_db)
):
    """
    **Proceso automático que se ejecuta diariamente.**
    
    Recorre todos los alumnos matriculados y verifica:
    
    | Condición | Acción |
    |-----------|--------|
    | 3 faltas acumuladas | Genera alerta SMS al apoderado |
    | 5 faltas acumuladas | Genera PDF de Citación para imprimir |
    | 3 justificaciones virtuales consecutivas | Alerta de bloqueo virtual |
    
    ⚠️ **Configuración recomendada:**
    - Ejecutar este endpoint con un CRON job diario a las 6:00 AM
    - O usar APScheduler dentro de FastAPI
    
    **No genera duplicados:** Si ya se envió una alerta del mismo tipo 
    hoy para el mismo alumno, la omite.
    """
    return await services.disparar_alertas_automaticas(db)


# ═══════════════════════════════════════════════════════════════
# CONSULTAS
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/",
    response_model=List[AlertaCardResponse],
    summary="Listar todas las alertas"
)
async def listar_alertas(
    tipo: Optional[str] = Query(None, description="Filtrar: sms_3_faltas, citacion_5_faltas, justificacion_bloqueada"),
    estado: Optional[str] = Query(None, description="Filtrar: enviada, entregada, fallida"),
    alumno_id: Optional[int] = Query(None, description="Filtrar por alumno"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Lista todas las alertas con filtros opcionales."""
    return await services.obtener_todas_las_alertas(
        db=db, skip=skip, limit=limit, tipo=tipo, estado=estado, alumno_id=alumno_id
    )


@router.get(
    "/{alerta_id}",
    response_model=AlertaResponse,
    summary="Ver alerta por ID"
)
async def ver_alerta(
    alerta_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el detalle completo de una alerta con el mensaje SMS."""
    alerta = await services.obtener_alerta_por_id(db, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada.")
    return alerta


@router.get(
    "/alumno/{alumno_id}",
    response_model=List[AlertaCardResponse],
    summary="Historial de alertas de un alumno"
)
async def alertas_por_alumno(
    alumno_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todas las alertas generadas para un alumno específico."""
    alertas = await services.obtener_alertas_por_alumno(db, alumno_id)
    if not alertas:
        return []
    return alertas


@router.get(
    "/apoderado/{apoderado_id}",
    response_model=List[AlertaCardResponse],
    summary="Alertas recibidas por un apoderado"
)
async def alertas_por_apoderado(
    apoderado_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Alertas que ha recibido un apoderado.**
    
    Útil para la App Familiar: el padre puede ver el historial
    de alertas de todos sus hijos.
    """
    alertas = await services.obtener_alertas_por_apoderado(db, apoderado_id)
    if not alertas:
        return []
    return alertas


# ═══════════════════════════════════════════════════════════════
# OPERACIONES
# ═══════════════════════════════════════════════════════════════

@router.patch(
    "/{alerta_id}/entregar",
    response_model=AlertaResponse,
    summary="Marcar alerta como entregada"
)
async def marcar_alerta_entregada(
    alerta_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Marca una alerta como entregada.**
    
    - **SMS**: Cuando el proveedor confirma la entrega al celular
    - **Citación PDF**: Cuando el Auxiliar imprime y entrega físicamente la citación
    
    Esto actualiza el estado de 'enviada' a 'entregada' y registra la fecha.
    """
    return await services.marcar_alerta_como_entregada(db, alerta_id)


# ═══════════════════════════════════════════════════════════════
# ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/estadisticas/generales",
    response_model=EstadisticasAlertasResponse,
    summary="Estadísticas generales de alertas"
)
async def estadisticas_alertas(
    db: AsyncSession = Depends(get_db)
):
    """Estadísticas generales para el dashboard administrativo."""
    return await services.obtener_estadisticas_alertas(db)