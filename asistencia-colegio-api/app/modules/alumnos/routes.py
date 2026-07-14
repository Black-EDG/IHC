from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.modules.alumnos import services
from app.modules.alumnos.schemas import (
    AlumnoCreate,
    AlumnoResponse,
    AlumnoUpdate,
    AlumnoCardResponse,
    AlumnoResumenAsistenciaResponse,
    AlumnoBusquedaResponse,
    SuspensionRequest,
    TrasladoRequest
)

router = APIRouter(
    prefix="/alumnos",
    tags=["🎒 Alumnos / Estudiantes"]
)

# ═══════════════════════════════════════════════════════════════
# CRUD BÁSICO
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/", 
    response_model=AlumnoResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Matricular nuevo alumno"
)
async def matricular_alumno(
    alumno_in: AlumnoCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    **Registra un nuevo alumno en el sistema escolar.**
    
    El Admin registra al alumno con:
    - DNI del alumno
    - Nombres y apellidos
    - Género y fecha de nacimiento
    - Aula donde se matricula
    - Apoderado responsable (debe estar registrado previamente)
    """
    return await services.crear_alumno(db=db, alumno_data=alumno_in)

@router.get(
    "/", 
    response_model=List[AlumnoCardResponse],
    summary="Listar todos los alumnos"
)
async def listar_alumnos(
    estado: Optional[str] = Query(None, description="Filtrar por estado: matriculado, trasladado, retirado"),
    aula_id: Optional[int] = Query(None, description="Filtrar por aula específica"),
    grado: Optional[int] = Query(None, ge=1, le=5, description="Filtrar por grado (1-5)"),
    buscar: Optional[str] = Query(None, description="Buscar por DNI o nombre"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    **Lista todos los alumnos con filtros avanzados.**
    
    Filtros disponibles:
    - **estado**: matriculado, trasladado, retirado
    - **aula_id**: ID del aula específica
    - **grado**: 1 al 5
    - **buscar**: búsqueda por DNI o nombre
    """
    return await services.obtener_todos_los_alumnos(
        db=db, 
        skip=skip, 
        limit=limit, 
        estado=estado,
        aula_id=aula_id,
        grado=grado,
        buscar=buscar
    )

@router.get(
    "/buscar", 
    response_model=List[AlumnoBusquedaResponse],
    summary="Búsqueda rápida de alumnos"
)
async def buscar_alumnos(
    query: str = Query(..., min_length=2, description="DNI o nombre del alumno"),
    db: AsyncSession = Depends(get_db)
):
    """
    **Búsqueda rápida para autocompletado en formularios.**
    """
    return await services.obtener_todos_los_alumnos(db=db, buscar=query, limit=10)

@router.get(
    "/aula/{aula_id}", 
    response_model=List[AlumnoCardResponse],
    summary="Alumnos por aula"
)
async def alumnos_por_aula(
    aula_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Obtiene todos los alumnos de un aula específica.**
    
    Usado por:
    - Docentes para pasar asistencia
    - Tutores para revisar su sección
    - Auxiliares para monitoreo diario
    """
    alumnos = await services.obtener_alumnos_por_aula(db=db, aula_id=aula_id)
    if not alumnos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron alumnos en el aula ID {aula_id}."
        )
    return alumnos

@router.get(
    "/apoderado/{apoderado_id}", 
    response_model=List[AlumnoCardResponse],
    summary="Hijos de un apoderado"
)
async def hijos_por_apoderado(
    apoderado_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Obtiene todos los hijos de un apoderado.**
    
    Alimenta la bandeja de selección en la App Familiar.
    """
    alumnos = await services.obtener_alumnos_por_apoderado(db=db, apoderado_id=apoderado_id)
    if not alumnos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron alumnos para el apoderado ID {apoderado_id}."
        )
    return alumnos

@router.get(
    "/dni/{dni}", 
    response_model=AlumnoResponse,
    summary="Buscar alumno por DNI"
)
async def alumno_por_dni(
    dni: str,
    db: AsyncSession = Depends(get_db)
):
    """Busca la información completa de un alumno por su DNI."""
    if len(dni) != 8 or not dni.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DNI inválido. Debe contener 8 dígitos."
        )
    
    alumno = await services.obtener_alumno_por_dni(db=db, dni=dni)
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró alumno con DNI {dni}."
        )
    return alumno

@router.get(
    "/{alumno_id}", 
    response_model=AlumnoResponse,
    summary="Ver alumno por ID"
)
async def ver_alumno(
    alumno_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene los datos completos de un alumno por su ID."""
    alumno = await services.obtener_alumno_por_id(db=db, alumno_id=alumno_id)
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alumno con ID {alumno_id} no encontrado."
        )
    return alumno

@router.patch(
    "/{alumno_id}", 
    response_model=AlumnoResponse,
    summary="Actualizar datos del alumno"
)
async def actualizar_alumno(
    alumno_id: int,
    alumno_in: AlumnoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza los datos de un alumno existente."""
    alumno = await services.actualizar_alumno(db=db, alumno_id=alumno_id, alumno_data=alumno_in)
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alumno con ID {alumno_id} no encontrado."
        )
    return alumno

@router.delete(
    "/{alumno_id}",
    summary="Eliminar alumno"
)
async def eliminar_alumno(
    alumno_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Elimina permanentemente a un alumno.**
    
    ⚠️ Solo se puede eliminar si no tiene asistencias registradas.
    Si tiene historial, se recomienda cambiar su estado a 'retirado'.
    """
    resultado = await services.eliminar_alumno(db=db, alumno_id=alumno_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alumno con ID {alumno_id} no encontrado."
        )
    return {
        "mensaje": "Alumno eliminado correctamente del sistema.",
        "status": "success"
    }

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE NEGOCIO
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/{alumno_id}/suspender",
    response_model=AlumnoResponse,
    summary="Suspender alumno"
)
async def suspender_alumno(
    alumno_id: int,
    suspension: SuspensionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    **Suspende a un alumno por indisciplina u otra razón.**
    
    - Máximo 30 días de suspensión
    - Solo se puede suspender a alumnos matriculados
    - Las fechas deben ser desde hoy en adelante
    """
    return await services.suspender_alumno(db=db, alumno_id=alumno_id, suspension=suspension)

@router.post(
    "/{alumno_id}/levantar-suspension",
    response_model=AlumnoResponse,
    summary="Levantar suspensión"
)
async def levantar_suspension_alumno(
    alumno_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Elimina la suspensión activa de un alumno.**
    
    El alumno vuelve a estar habilitado para asistir a clases.
    """
    return await services.levantar_suspension(db=db, alumno_id=alumno_id)

@router.post(
    "/{alumno_id}/trasladar",
    response_model=AlumnoResponse,
    summary="Trasladar alumno de aula"
)
async def trasladar_alumno(
    alumno_id: int,
    traslado: TrasladoRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    **Traslada a un alumno a otra aula.**
    
    Usado cuando:
    - Cambio de sección por indisciplina
    - Reorganización de aulas
    - Solicitud del padre de familia
    """
    return await services.trasladar_alumno(db=db, alumno_id=alumno_id, traslado=traslado)

@router.post(
    "/{alumno_id}/retirar",
    response_model=AlumnoResponse,
    summary="Retirar alumno del colegio"
)
async def retirar_alumno(
    alumno_id: int,
    motivo: Optional[str] = Query(None, description="Motivo del retiro"),
    db: AsyncSession = Depends(get_db)
):
    """
    **Retira oficialmente al alumno del colegio.**
    
    Cambia el estado a 'retirado' y elimina cualquier suspensión activa.
    El historial de asistencias se mantiene para registros.
    """
    return await services.retirar_alumno(db=db, alumno_id=alumno_id, motivo=motivo)

# ═══════════════════════════════════════════════════════════════
# REPORTES Y ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/{alumno_id}/asistencias",
    response_model=AlumnoResumenAsistenciaResponse,
    summary="Resumen de asistencias del alumno"
)
async def resumen_asistencias_alumno(
    alumno_id: int,
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    **Obtiene el resumen de asistencias de un alumno.**
    
    Si no se especifican fechas, se toma el año actual.
    
    Retorna:
    - Total de asistencias registradas
    - Cantidad de presentes, ausentes, tardes y justificados
    - Porcentaje de asistencia
    - Indicador de riesgo de inhabilitación (>30% de faltas)
    """
    from datetime import date as date_type
    
    fi = date_type.fromisoformat(fecha_inicio) if fecha_inicio else None
    ff = date_type.fromisoformat(fecha_fin) if fecha_fin else None
    
    return await services.obtener_resumen_asistencias(
        db=db, 
        alumno_id=alumno_id,
        fecha_inicio=fi,
        fecha_fin=ff
    )

@router.get(
    "/estadisticas/generales",
    summary="Estadísticas generales de alumnos"
)
async def estadisticas_generales(
    db: AsyncSession = Depends(get_db)
):
    """
    **Obtiene estadísticas generales para el dashboard administrativo.**
    
    Incluye:
    - Total de alumnos por estado
    - Alumnos suspendidos actualmente
    - Distribución por grado
    """
    return await services.obtener_estadisticas_generales(db=db)

# ═══════════════════════════════════════════════════════════════
# PROCESO MASIVO DE PROMOCIÓN (FIN DE AÑO)
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/promocion/{anio_actual}",
    summary="🚀 Proceso de Promoción Masiva (Fin de Año)"
)
async def promocion_masiva(
    anio_actual: int,
    db: AsyncSession = Depends(get_db)
):
    """
    **Ejecuta la promoción automática de todos los alumnos al siguiente grado.**
    
    ⚠️ **Este proceso se ejecuta UNA VEZ al finalizar el año escolar.**
    
    **Lógica:**
    - Alumnos de 1° a 4°: Pasan al siguiente grado en la misma sección
    - Alumnos de 5°: Se gradúan (estado 'retirado')
    - Alumnos retirados/trasladados: No se procesan
    
    **Requisitos:**
    - Las aulas del siguiente año deben estar creadas previamente
    """
    return await services.proceso_promocion_masiva(db=db, anio_actual=anio_actual)