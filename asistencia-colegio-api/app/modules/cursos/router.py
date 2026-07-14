from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.modules.cursos import services
from app.modules.cursos.schemas import (
    CursoCreate,
    CursoResponse,
    CursoUpdate,
    CursoCardResponse,
    CursoBusquedaResponse,
    CursoCreateMultiple
)

router = APIRouter(
    prefix="/cursos",
    tags=["📚 Cursos / Materias"]
)

# ═══════════════════════════════════════════════════════════════
# CRUD BÁSICO
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/", 
    response_model=CursoResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo curso"
)
async def crear_curso(
    curso_in: CursoCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Crea un nuevo curso en el sistema."""
    return await services.crear_curso(db=db, curso_data=curso_in)


@router.post(
    "/crear-multiples",
    status_code=status.HTTP_201_CREATED,
    summary="Crear múltiples cursos a la vez"
)
async def crear_cursos_multiples(
    data: CursoCreateMultiple,
    db: AsyncSession = Depends(get_db)
):
    """Crea varios cursos de una sola vez."""
    return await services.crear_cursos_multiples(db=db, cursos_data=data.cursos)


@router.get(
    "/", 
    response_model=List[CursoCardResponse],
    summary="Listar todos los cursos"
)
async def listar_cursos(
    buscar: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Lista todos los cursos registrados en el sistema."""
    return await services.obtener_todos_los_cursos(db=db, skip=skip, limit=limit, buscar=buscar)


@router.get(
    "/con-asignaciones", 
    response_model=List[CursoCardResponse],
    summary="Cursos con docentes asignados"
)
async def cursos_con_asignaciones(
    db: AsyncSession = Depends(get_db)
):
    """Lista solo los cursos que tienen al menos un docente asignado."""
    cursos = await services.obtener_cursos_con_asignaciones(db=db)
    return cursos


@router.get(
    "/buscar", 
    response_model=List[CursoBusquedaResponse],
    summary="Búsqueda rápida de cursos"
)
async def buscar_cursos(
    query: str = Query(..., min_length=2, description="Nombre del curso a buscar"),
    db: AsyncSession = Depends(get_db)
):
    """Búsqueda rápida para autocompletado en formularios."""
    return await services.obtener_todos_los_cursos(db=db, buscar=query, limit=10)


@router.get(
    "/docente/{usuario_id}", 
    response_model=List[CursoCardResponse],
    summary="Cursos por docente"
)
async def cursos_por_docente(
    usuario_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todos los cursos que imparte un docente específico."""
    cursos = await services.obtener_cursos_por_docente(db=db, usuario_id=usuario_id)
    if not cursos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El docente con ID {usuario_id} no tiene cursos asignados."
        )
    return cursos


@router.get(
    "/{curso_id}", 
    response_model=CursoResponse,
    summary="Ver curso por ID"
)
async def ver_curso(
    curso_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene los datos completos de un curso por su ID."""
    curso = await services.obtener_curso_por_id(db=db, curso_id=curso_id)
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado."
        )
    return curso


@router.get(
    "/{curso_id}/estadisticas",
    summary="Estadísticas del curso"
)
async def estadisticas_curso(
    curso_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene estadísticas detalladas de un curso."""
    return await services.obtener_estadisticas_curso(db=db, curso_id=curso_id)


@router.patch(
    "/{curso_id}", 
    response_model=CursoResponse,
    summary="Actualizar curso"
)
async def actualizar_curso(
    curso_id: int,
    curso_in: CursoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza los datos de un curso existente."""
    curso = await services.actualizar_curso(db=db, curso_id=curso_id, curso_data=curso_in)
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado."
        )
    return curso


@router.delete(
    "/{curso_id}",
    summary="Eliminar curso"
)
async def eliminar_curso(
    curso_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Elimina permanentemente un curso del sistema."""
    resultado = await services.eliminar_curso(db=db, curso_id=curso_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado."
        )
    return {
        "mensaje": "Curso eliminado correctamente del sistema.",
        "status": "success",
        "curso_id": curso_id
    }