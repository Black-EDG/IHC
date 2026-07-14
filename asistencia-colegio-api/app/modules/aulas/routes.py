from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date as date_type
from app.core.database import get_db
from app.modules.aulas import services
from app.modules.aulas.schemas import (
    AulaCreate,
    AulaResponse,
    AulaUpdate,
    AulaCardResponse,
    ListadoAulaResponse,
    AsistenciaAulaResponse,
    CrearAulasPorGradoRequest,
    AulaEstadisticasResponse
)

router = APIRouter(
    prefix="/aulas",
    tags=["🏫 Aulas / Salones"]
)

# ═══════════════════════════════════════════════════════════════
# CRUD BÁSICO
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/", 
    response_model=AulaResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva aula"
)
async def crear_aula(
    aula_in: AulaCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Crea una nueva aula en el sistema."""
    return await services.crear_aula(db=db, aula_data=aula_in)


@router.post(
    "/crear-por-grado",
    status_code=status.HTTP_201_CREATED,
    summary="Crear múltiples secciones por grado"
)
async def crear_aulas_por_grado(
    data: CrearAulasPorGradoRequest,
    db: AsyncSession = Depends(get_db)
):
    """Crea todas las secciones de un grado de una sola vez."""
    return await services.crear_aulas_por_grado(db=db, data=data)


@router.get(
    "/", 
    response_model=List[AulaCardResponse],
    summary="Listar todas las aulas"
)
async def listar_aulas(
    anio_escolar: Optional[int] = Query(None, description="Filtrar por año escolar"),
    grado: Optional[int] = Query(None, ge=1, le=5, description="Filtrar por grado"),
    turno: Optional[str] = Query(None, description="Filtrar por turno"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Lista todas las aulas con filtros opcionales."""
    return await services.obtener_todas_las_aulas(
        db=db,
        anio_escolar=anio_escolar,
        grado=grado,
        turno=turno,
        skip=skip,
        limit=limit
    )


@router.get(
    "/anio/{anio_escolar}", 
    response_model=List[AulaCardResponse],
    summary="Aulas por año escolar"
)
async def aulas_por_anio(
    anio_escolar: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todas las aulas de un año escolar específico."""
    aulas = await services.obtener_aulas_por_anio(db=db, anio_escolar=anio_escolar)
    if not aulas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron aulas para el año escolar {anio_escolar}."
        )
    return aulas


@router.get(
    "/grado/{grado}", 
    response_model=List[AulaCardResponse],
    summary="Aulas por grado"
)
async def aulas_por_grado(
    grado: int,
    anio_escolar: Optional[int] = Query(None, description="Año escolar específico"),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todas las secciones de un grado específico."""
    if grado < 1 or grado > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El grado debe estar entre 1 y 5 (secundaria)."
        )
    aulas = await services.obtener_aulas_por_grado(db=db, grado=grado, anio_escolar=anio_escolar)
    if not aulas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron secciones para {grado}° grado."
        )
    return aulas


@router.get(
    "/buscar", 
    response_model=AulaResponse,
    summary="Buscar aula específica"
)
async def buscar_aula(
    grado: int = Query(..., ge=1, le=5, description="Grado: 1-5"),
    seccion: str = Query(..., min_length=1, max_length=2, description="Sección: A, B, C..."),
    anio_escolar: int = Query(..., description="Año escolar"),
    db: AsyncSession = Depends(get_db)
):
    """Busca un aula específica por grado, sección y año."""
    aula = await services.obtener_aula_por_grado_seccion(
        db=db, grado=grado, seccion=seccion.upper(), anio_escolar=anio_escolar
    )
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula {grado}° {seccion.upper()} no encontrada para el año {anio_escolar}."
        )
    return aula


@router.get(
    "/{aula_id}", 
    response_model=AulaResponse,
    summary="Ver aula por ID"
)
async def ver_aula(
    aula_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene los datos completos de un aula por su ID."""
    aula = await services.obtener_aula_por_id(db=db, aula_id=aula_id)
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula con ID {aula_id} no encontrada."
        )
    return aula


@router.patch(
    "/{aula_id}", 
    response_model=AulaResponse,
    summary="Actualizar aula"
)
async def actualizar_aula(
    aula_id: int,
    aula_in: AulaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza los datos de un aula (solo se puede cambiar el turno)."""
    aula = await services.actualizar_aula(db=db, aula_id=aula_id, aula_data=aula_in)
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula con ID {aula_id} no encontrada."
        )
    return aula


@router.delete(
    "/{aula_id}",
    summary="Eliminar aula"
)
async def eliminar_aula(
    aula_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Elimina permanentemente un aula (debe estar vacía)."""
    resultado = await services.eliminar_aula(db=db, aula_id=aula_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula con ID {aula_id} no encontrada."
        )
    return {
        "mensaje": "Aula eliminada correctamente del sistema.",
        "status": "success"
    }


# ═══════════════════════════════════════════════════════════════
# LISTADOS Y ASISTENCIAS DEL AULA
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/{aula_id}/listado",
    response_model=ListadoAulaResponse,
    summary="Listado completo del aula"
)
async def listado_aula(
    aula_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el listado completo de alumnos del aula ordenado alfabéticamente."""
    return await services.obtener_listado_aula(db=db, aula_id=aula_id)


@router.get(
    "/{aula_id}/asistencia",
    response_model=AsistenciaAulaResponse,
    summary="Asistencia del aula por fecha"
)
async def asistencia_aula_fecha(
    aula_id: int,
    fecha: Optional[str] = Query(None, description="Fecha (YYYY-MM-DD). Por defecto: hoy"),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el resumen de asistencia del aula en una fecha específica."""
    fecha_obj = date_type.fromisoformat(fecha) if fecha else None
    return await services.obtener_asistencia_aula_fecha(db=db, aula_id=aula_id, fecha=fecha_obj)


@router.get(
    "/{aula_id}/estadisticas",
    response_model=AulaEstadisticasResponse,
    summary="Estadísticas del aula"
)
async def estadisticas_aula(
    aula_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene estadísticas detalladas del aula para el dashboard."""
    return await services.obtener_estadisticas_aula(db=db, aula_id=aula_id)


# ═══════════════════════════════════════════════════════════════
# PROCESOS MASIVOS
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/crear-siguiente-anio/{anio_actual}",
    summary="Crear aulas para el siguiente año escolar"
)
async def crear_aulas_siguiente_anio(
    anio_actual: int,
    secciones: Optional[str] = Query('A,B,C,D,E', description="Secciones separadas por coma"),
    db: AsyncSession = Depends(get_db)
):
    """Crea automáticamente la estructura de aulas para el siguiente año escolar."""
    lista_secciones = [s.strip().upper()[:2] for s in secciones.split(',')]
    return await services.proceso_crear_aulas_siguiente_anio(
        db=db,
        anio_actual=anio_actual,
        secciones_por_defecto=lista_secciones
    )


@router.get(
    "/estadisticas/por-grado/{anio_escolar}",
    summary="Estadísticas por grado"
)
async def estadisticas_por_grado(
    anio_escolar: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene estadísticas agrupadas por grado para un año escolar."""
    return await services.obtener_estadisticas_por_grado(db=db, anio_escolar=anio_escolar)