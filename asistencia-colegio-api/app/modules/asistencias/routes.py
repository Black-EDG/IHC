from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date as date_type
from app.core.database import get_db
from app.modules.asistencias import services
from app.modules.asistencias.schemas import (
    AsistenciaIndividualCreate,
    AsistenciaMasivaCreate,
    AsistenciaUpdate,
    AsistenciaResponse,
    AsistenciaDetalleResponse,
    ResumenAsistenciaAulaResponse,
    ResumenAsistenciaAlumnoResponse,
    EstadisticasGeneralesResponse
)

router = APIRouter(
    prefix="/asistencias",
    tags=["✅ Asistencias"]
)

# ═══════════════════════════════════════════════════════════════
# REGISTRO DE ASISTENCIAS
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/individual",
    response_model=AsistenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar asistencia individual"
)
async def registrar_asistencia_individual(
    data: AsistenciaIndividualCreate,
    usuario_id: int = Query(..., description="ID del usuario que registra"),
    curso_id: Optional[int] = Query(None, description="ID del curso (NULL = General)"),
    aula_id: Optional[int] = Query(None, description="ID del aula"),
    db: AsyncSession = Depends(get_db)
):
    """Registra la asistencia de un solo alumno (correcciones o llegadas tarde)."""
    return await services.registrar_asistencia_individual(
        db=db, usuario_id=usuario_id, data=data, curso_id=curso_id, aula_id=aula_id
    )


@router.post(
    "/masiva",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar asistencia masiva del aula"
)
async def registrar_asistencia_masiva(
    data: AsistenciaMasivaCreate,
    usuario_id: int = Query(..., description="ID del usuario que registra"),
    db: AsyncSession = Depends(get_db)
):
    """
    **Registra la asistencia de todos los alumnos de un aula.**
    
    - **Auxiliar**: `curso_id=NULL` → Asistencia General del día
    - **Docente**: `curso_id=5` → Asistencia de su curso (Matemática, etc.)
    """
    return await services.registrar_asistencia_masiva(db=db, usuario_id=usuario_id, data=data)


@router.patch(
    "/{asistencia_id}",
    response_model=AsistenciaResponse,
    summary="Actualizar asistencia"
)
async def actualizar_asistencia(
    asistencia_id: int,
    data: AsistenciaUpdate,
    usuario_id: int = Query(..., description="ID del usuario que modifica"),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza el estado de una asistencia existente (solo Auxiliar puede modificar general)."""
    resultado = await services.actualizar_asistencia(
        db=db, asistencia_id=asistencia_id, usuario_id=usuario_id, data=data
    )
    if not resultado:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada.")
    return resultado


# ═══════════════════════════════════════════════════════════════
# CONSULTAS DE ASISTENCIAS
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/{asistencia_id}",
    response_model=AsistenciaDetalleResponse,
    summary="Ver asistencia por ID"
)
async def ver_asistencia(
    asistencia_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el detalle completo de un registro de asistencia."""
    asistencia = await services.obtener_asistencia_por_id(db, asistencia_id)
    if not asistencia:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada.")
    return asistencia.resumen_asistencia()


@router.get(
    "/aula/{aula_id}",
    response_model=ResumenAsistenciaAulaResponse,
    summary="Resumen de asistencia del aula"
)
async def resumen_aula(
    aula_id: int,
    fecha: Optional[str] = Query(None, description="Fecha (YYYY-MM-DD). Default: hoy"),
    curso_id: Optional[int] = Query(None, description="Filtrar por curso (NULL = General)"),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el resumen de asistencia de un aula en una fecha."""
    fecha_obj = date_type.fromisoformat(fecha) if fecha else date_type.today()
    return await services.obtener_resumen_aula_fecha(
        db=db, aula_id=aula_id, fecha=fecha_obj, curso_id=curso_id
    )


@router.get(
    "/alumno/{alumno_id}",
    response_model=ResumenAsistenciaAlumnoResponse,
    summary="Historial de asistencias del alumno"
)
async def historial_alumno(
    alumno_id: int,
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    **Obtiene el historial completo de asistencias de un alumno.**
    
    Incluye:
    - Conteo de presentes, ausentes, tardes, justificados
    - Porcentaje de asistencia
    - Indicador de riesgo de inhabilitación (>30% faltas)
    - Faltas consecutivas y justificaciones virtuales disponibles
    """
    fi = date_type.fromisoformat(fecha_inicio) if fecha_inicio else None
    ff = date_type.fromisoformat(fecha_fin) if fecha_fin else None
    return await services.obtener_resumen_alumno_periodo(
        db=db, alumno_id=alumno_id, fecha_inicio=fi, fecha_fin=ff
    )


@router.get(
    "/alumno/{alumno_id}/detalle",
    response_model=List[AsistenciaDetalleResponse],
    summary="Lista detallada de asistencias del alumno"
)
async def detalle_asistencias_alumno(
    alumno_id: int,
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    solo_faltas: bool = Query(False, description="Solo mostrar inasistencias"),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene la lista detallada de todas las asistencias de un alumno."""
    fi = date_type.fromisoformat(fecha_inicio) if fecha_inicio else None
    ff = date_type.fromisoformat(fecha_fin) if fecha_fin else None
    
    asistencias = await services.obtener_asistencias_por_alumno(
        db=db, alumno_id=alumno_id, fecha_inicio=fi, fecha_fin=ff, solo_faltas=solo_faltas
    )
    return [a.resumen_asistencia() for a in asistencias]


@router.get(
    "/estadisticas/hoy",
    response_model=EstadisticasGeneralesResponse,
    summary="Estadísticas generales de hoy"
)
async def estadisticas_hoy(
    db: AsyncSession = Depends(get_db)
):
    """Obtiene estadísticas generales de asistencia del día actual."""
    return await services.obtener_estadisticas_generales_hoy(db=db)