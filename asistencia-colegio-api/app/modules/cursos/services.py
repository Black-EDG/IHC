from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.cursos.models import Curso
from app.modules.cursos.schemas import CursoCreate, CursoUpdate

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════

async def obtener_curso_por_id(db: AsyncSession, curso_id: int) -> Optional[Curso]:
    """Busca un curso por su ID con todas las relaciones precargadas"""
    resultado = await db.execute(
        select(Curso)
        .options(
            selectinload(Curso.asignaciones),
            selectinload(Curso.asistencias)
        )
        .where(Curso.id == curso_id)
    )
    return resultado.scalars().first()

async def obtener_curso_por_nombre(db: AsyncSession, nombre: str) -> Optional[Curso]:
    """Busca un curso por su nombre exacto (case insensitive)"""
    from sqlalchemy import func
    resultado = await db.execute(
        select(Curso)
        .where(func.lower(Curso.nombre) == nombre.lower().strip())
    )
    return resultado.scalars().first()

async def obtener_todos_los_cursos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    buscar: Optional[str] = None
) -> List[Curso]:
    """
    Lista todos los cursos con búsqueda opcional por nombre o descripción.
    """
    query = select(Curso).options(
        selectinload(Curso.asignaciones)
    )
    
    if buscar:
        search_term = f"%{buscar}%"
        query = query.where(
            or_(
                Curso.nombre.ilike(search_term),
                Curso.descripcion.ilike(search_term)
            )
        )
    
    query = query.order_by(Curso.nombre).offset(skip).limit(limit)
    resultado = await db.execute(query)
    return resultado.scalars().all()

async def obtener_cursos_con_asignaciones(db: AsyncSession) -> List[Curso]:
    """
    Obtiene todos los cursos que tienen al menos un docente asignado.
    Útil para mostrar solo cursos activos en el año escolar.
    """
    resultado = await db.execute(
        select(Curso)
        .options(selectinload(Curso.asignaciones))
        .where(Curso.asignaciones.any())
        .order_by(Curso.nombre)
    )
    return resultado.scalars().all()

# ═══════════════════════════════════════════════════════════════
# OPERACIONES CRUD
# ═══════════════════════════════════════════════════════════════

async def crear_curso(db: AsyncSession, curso_data: CursoCreate) -> Curso:
    """
    Crea un nuevo curso con validación de nombre único.
    """
    # Validar que no exista un curso con el mismo nombre
    existente = await obtener_curso_por_nombre(db, curso_data.nombre)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El curso '{curso_data.nombre}' ya existe en el sistema. "
                    f"ID del curso existente: {existente.id}"
        )
    
    datos = curso_data.model_dump()
    nuevo_curso = Curso(**datos)
    
    db.add(nuevo_curso)
    await db.commit()
    await db.refresh(nuevo_curso)
    
    return nuevo_curso

async def crear_cursos_multiples(
    db: AsyncSession, 
    cursos_data: List[CursoCreate]
) -> dict:
    """
    Crea múltiples cursos a la vez.
    Retorna lista de creados y errores si los hubo.
    """
    cursos_creados = []
    errores = []
    
    for curso_data in cursos_data:
        try:
            curso = await crear_curso(db, curso_data)
            cursos_creados.append({
                "id": curso.id,
                "nombre": curso.nombre
            })
        except HTTPException as e:
            errores.append({
                "curso": curso_data.nombre,
                "error": e.detail
            })
    
    return {
        "total_solicitados": len(cursos_data),
        "creados": len(cursos_creados),
        "cursos_creados": cursos_creados,
        "errores": errores
    }

async def actualizar_curso(
    db: AsyncSession, 
    curso_id: int, 
    curso_data: CursoUpdate
) -> Optional[Curso]:
    """
    Actualiza los datos de un curso existente.
    """
    curso = await obtener_curso_por_id(db, curso_id)
    
    if not curso:
        return None
    
    update_data = curso_data.model_dump(exclude_unset=True)
    
    # Si se cambia el nombre, validar que no exista otro curso con ese nombre
    if 'nombre' in update_data and update_data['nombre'].lower() != curso.nombre.lower():
        existente = await obtener_curso_por_nombre(db, update_data['nombre'])
        if existente and existente.id != curso_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{update_data['nombre']}' ya está en uso por el curso ID {existente.id}."
            )
    
    for key, value in update_data.items():
        if hasattr(curso, key):
            setattr(curso, key, value)
    
    await db.commit()
    await db.refresh(curso)
    return curso

async def eliminar_curso(db: AsyncSession, curso_id: int) -> bool:
    """
    Elimina un curso solo si no tiene asignaciones ni asistencias vinculadas.
    """
    curso = await obtener_curso_por_id(db, curso_id)
    
    if not curso:
        return False
    
    # Verificar asignaciones
    if curso.asignaciones:
        aulas_asignadas = []
        for a in curso.asignaciones:
            if hasattr(a, 'aula') and a.aula:
                aulas_asignadas.append(a.aula.nombre_corto if hasattr(a.aula, 'nombre_corto') else f"ID {a.aula_id}")
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar el curso '{curso.nombre}' porque tiene "
                    f"{len(curso.asignaciones)} asignaciones activas en las aulas: "
                    f"{', '.join(aulas_asignadas[:5])}{'...' if len(aulas_asignadas) > 5 else ''}. "
                    "Elimine primero las asignaciones."
        )
    
    # Verificar asistencias
    if curso.asistencias:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar el curso '{curso.nombre}' porque tiene "
                    f"{len(curso.asistencias)} registros de asistencia vinculados. "
                    "Considere mantener el curso para preservar el historial académico."
        )
    
    await db.delete(curso)
    await db.commit()
    return True

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE NEGOCIO
# ═══════════════════════════════════════════════════════════════

async def obtener_estadisticas_curso(db: AsyncSession, curso_id: int) -> dict:
    """
    Obtiene estadísticas detalladas de un curso para el dashboard.
    """
    curso = await obtener_curso_por_id(db, curso_id)
    
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado."
        )
    
    # Agrupar asignaciones por año escolar
    asignaciones_por_anio = {}
    for asignacion in curso.asignaciones:
        if hasattr(asignacion, 'aula') and asignacion.aula:
            anio = asignacion.aula.anio_escolar
            if anio not in asignaciones_por_anio:
                asignaciones_por_anio[anio] = []
            asignaciones_por_anio[anio].append({
                "aula": asignacion.aula.nombre_corto if hasattr(asignacion.aula, 'nombre_corto') else f"ID {asignacion.aula_id}",
                "docente": asignacion.usuario.nombre_completo if hasattr(asignacion, 'usuario') and asignacion.usuario else "Sin asignar"
            })
    
    return {
        "curso": curso.nombre,
        "descripcion": curso.descripcion,
        "total_docentes": curso.cantidad_docentes_asignados,
        "total_aulas": curso.cantidad_aulas_asignadas,
        "total_asistencias": curso.total_asistencias_registradas,
        "asignaciones_por_anio": asignaciones_por_anio
    }

async def obtener_cursos_por_docente(db: AsyncSession, usuario_id: int) -> List[Curso]:
    """
    Obtiene todos los cursos que imparte un docente específico.
    """
    from app.modules.asignaciones.models import AsignacionAula
    
    resultado = await db.execute(
        select(Curso)
        .join(AsignacionAula)
        .where(
            AsignacionAula.usuario_id == usuario_id,
            AsignacionAula.tipo_cargo == 'docente_curso'
        )
        .distinct()
        .order_by(Curso.nombre)
    )
    return resultado.scalars().all()