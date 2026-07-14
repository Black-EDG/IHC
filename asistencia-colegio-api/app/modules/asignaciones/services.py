from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import date

from app.modules.asignaciones.models import AsignacionAula, TipoResponsabilidad
from app.modules.asignaciones.schemas import (
    AsignacionCreate,
    AsignacionUpdate,
    AsignacionMasivaRequest
)
from app.modules.usuarios.models import Usuario, RolUsuario
from app.modules.aulas.models import Aula
from app.modules.cursos.models import Curso

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════

async def obtener_asignacion_por_id(db: AsyncSession, asignacion_id: int) -> Optional[AsignacionAula]:
    """Busca una asignación por ID con todas las relaciones"""
    resultado = await db.execute(
        select(AsignacionAula)
        .options(
            selectinload(AsignacionAula.usuario),
            selectinload(AsignacionAula.aula),
            selectinload(AsignacionAula.curso)
        )
        .where(AsignacionAula.id == asignacion_id)
    )
    return resultado.scalars().first()

async def obtener_asignaciones_por_usuario(
    db: AsyncSession, 
    usuario_id: int,
    tipo_cargo: Optional[str] = None,
    anio_escolar: Optional[int] = None
) -> List[AsignacionAula]:
    """
    Obtiene todas las asignaciones de un usuario.
    Este es el endpoint principal del dashboard del docente al iniciar sesión.
    """
    condiciones = [AsignacionAula.usuario_id == usuario_id]
    
    if tipo_cargo:
        condiciones.append(AsignacionAula.tipo_cargo == tipo_cargo)
    
    query = select(AsignacionAula).options(
        selectinload(AsignacionAula.usuario),
        selectinload(AsignacionAula.aula),
        selectinload(AsignacionAula.curso)
    ).where(and_(*condiciones))
    
    if anio_escolar:
        query = query.join(Aula).where(Aula.anio_escolar == anio_escolar)
    
    query = query.order_by(AsignacionAula.tipo_cargo, Aula.grado, Aula.seccion)
    
    resultado = await db.execute(query)
    return resultado.scalars().all()

async def obtener_asignaciones_por_aula(
    db: AsyncSession, 
    aula_id: int
) -> List[AsignacionAula]:
    """Obtiene todas las asignaciones de un aula específica"""
    resultado = await db.execute(
        select(AsignacionAula)
        .options(
            selectinload(AsignacionAula.usuario),
            selectinload(AsignacionAula.curso)
        )
        .where(AsignacionAula.aula_id == aula_id)
        .order_by(AsignacionAula.tipo_cargo)
    )
    return resultado.scalars().all()

async def obtener_todas_las_asignaciones(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    anio_escolar: Optional[int] = None,
    tipo_cargo: Optional[str] = None
) -> List[AsignacionAula]:
    """Lista todas las asignaciones con filtros"""
    query = select(AsignacionAula).options(
        selectinload(AsignacionAula.usuario),
        selectinload(AsignacionAula.aula),
        selectinload(AsignacionAula.curso)
    )
    
    if anio_escolar:
        query = query.join(Aula).where(Aula.anio_escolar == anio_escolar)
    
    if tipo_cargo:
        query = query.where(AsignacionAula.tipo_cargo == tipo_cargo)
    
    query = query.order_by(
        Aula.anio_escolar.desc(),
        Aula.grado,
        Aula.seccion,
        AsignacionAula.tipo_cargo
    ).offset(skip).limit(limit)
    
    resultado = await db.execute(query)
    return resultado.scalars().all()

# ═══════════════════════════════════════════════════════════════
# OPERACIONES CRUD
# ═══════════════════════════════════════════════════════════════

async def crear_asignacion(db: AsyncSession, data: AsignacionCreate) -> AsignacionAula:
    """
    Crea una nueva asignación con todas las validaciones de negocio.
    """
    
    # Validar que el usuario exista y tenga el rol correcto
    usuario = await db.get(Usuario, data.usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario ID {data.usuario_id} no encontrado.")
    
    if usuario.estado != 'activo':
        raise HTTPException(status_code=400, detail=f"El usuario {usuario.nombre_completo} no está activo.")
    
    # Validar que el aula exista
    aula = await db.get(Aula, data.aula_id)
    if not aula:
        raise HTTPException(status_code=404, detail=f"Aula ID {data.aula_id} no encontrada.")
    
    # Validar curso si es docente
    if data.tipo_cargo == TipoResponsabilidad.DOCENTE_CURSO:
        if not data.curso_id:
            raise HTTPException(status_code=400, detail="Un docente de curso requiere curso_id.")
        
        curso = await db.get(Curso, data.curso_id)
        if not curso:
            raise HTTPException(status_code=404, detail=f"Curso ID {data.curso_id} no encontrado.")
        
        # Validar rol del usuario
        if usuario.rol not in [RolUsuario.docente, RolUsuario.admin]:
            raise HTTPException(
                status_code=400,
                detail=f"El usuario {usuario.nombre_completo} es {usuario.rol.value}. "
                        "Solo los docentes pueden dictar cursos."
            )
    
    # Validar que un tutor sea docente
    if data.tipo_cargo == TipoResponsabilidad.TUTOR_SECCION:
        if usuario.rol not in [RolUsuario.docente, RolUsuario.admin]:
            raise HTTPException(
                status_code=400,
                detail="Solo los docentes pueden ser tutores de sección."
            )
        
        # Verificar que no haya otro tutor en la misma aula
        tutor_existente = await db.execute(
            select(AsignacionAula).where(
                and_(
                    AsignacionAula.aula_id == data.aula_id,
                    AsignacionAula.tipo_cargo == TipoResponsabilidad.TUTOR_SECCION
                )
            )
        )
        if tutor_existente.scalars().first():
            raise HTTPException(
                status_code=409,
                detail=f"El aula {aula.nombre_corto} ya tiene un tutor asignado."
            )
    
    # Validar que un auxiliar sea auxiliar
    if data.tipo_cargo == TipoResponsabilidad.AUXILIAR_GRADO:
        if usuario.rol not in [RolUsuario.auxiliar, RolUsuario.admin]:
            raise HTTPException(
                status_code=400,
                detail="Solo los auxiliares pueden ser asignados como auxiliar de grado."
            )
    
    # Verificar duplicado (misma aula, mismo curso, mismo tipo)
    if data.tipo_cargo == TipoResponsabilidad.DOCENTE_CURSO:
        existente = await db.execute(
            select(AsignacionAula).where(
                and_(
                    AsignacionAula.aula_id == data.aula_id,
                    AsignacionAula.curso_id == data.curso_id,
                    AsignacionAula.tipo_cargo == data.tipo_cargo
                )
            )
        )
        if existente.scalars().first():
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un docente asignado a ese curso en el aula {aula.nombre_corto}."
            )
    
    # Crear asignación
    datos = data.model_dump()
    nueva_asignacion = AsignacionAula(**datos)
    
    db.add(nueva_asignacion)
    await db.commit()
    await db.refresh(nueva_asignacion)
    
    return nueva_asignacion

async def crear_asignacion_masiva(db: AsyncSession, data: AsignacionMasivaRequest) -> dict:
    """
    Asigna un docente a múltiples aulas para un mismo curso.
    Ejemplo: Profesor de Matemática a 1°A, 1°B, 1°C, 2°A, 2°B
    """
    asignaciones_creadas = []
    errores = []
    
    for aula_id in data.aulas_ids:
        try:
            asignacion = await crear_asignacion(db, AsignacionCreate(
                usuario_id=data.usuario_id,
                aula_id=aula_id,
                curso_id=data.curso_id,
                tipo_cargo=data.tipo_cargo
            ))
            asignaciones_creadas.append({
                "id": asignacion.id,
                "aula": asignacion.aula.nombre_corto if asignacion.aula else f"ID {aula_id}"
            })
        except HTTPException as e:
            errores.append({
                "aula_id": aula_id,
                "error": e.detail
            })
    
    return {
        "usuario_id": data.usuario_id,
        "curso_id": data.curso_id,
        "total_solicitados": len(data.aulas_ids),
        "creados": len(asignaciones_creadas),
        "asignaciones_creadas": asignaciones_creadas,
        "errores": errores
    }

async def actualizar_asignacion(
    db: AsyncSession, 
    asignacion_id: int, 
    data: AsignacionUpdate
) -> Optional[AsignacionAula]:
    """Actualiza los datos de una asignación existente"""
    asignacion = await obtener_asignacion_por_id(db, asignacion_id)
    
    if not asignacion:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if hasattr(asignacion, key):
            setattr(asignacion, key, value)
    
    await db.commit()
    await db.refresh(asignacion)
    return asignacion

async def eliminar_asignacion(db: AsyncSession, asignacion_id: int) -> bool:
    """Elimina una asignación"""
    asignacion = await obtener_asignacion_por_id(db, asignacion_id)
    
    if not asignacion:
        return False
    
    await db.delete(asignacion)
    await db.commit()
    return True

# ═══════════════════════════════════════════════════════════════
# DASHBOARD Y REPORTES
# ═══════════════════════════════════════════════════════════════

async def obtener_dashboard_docente(db: AsyncSession, usuario_id: int) -> dict:
    """
    Obtiene el dashboard completo de un docente al iniciar sesión.
    Organiza sus asignaciones en: docente_curso, tutor_seccion, auxiliar_grado
    """
    usuario = await db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    asignaciones = await obtener_asignaciones_por_usuario(db, usuario_id)
    
    docente = [a.to_card_response() for a in asignaciones if a.es_docente]
    tutor = [a.to_card_response() for a in asignaciones if a.es_tutor]
    auxiliar = [a.to_card_response() for a in asignaciones if a.es_auxiliar]
    
    return {
        "usuario_id": usuario_id,
        "usuario_nombre": usuario.nombre_completo,
        "usuario_rol": usuario.rol.value,
        "asignaciones_docente": docente,
        "asignaciones_tutor": tutor,
        "asignaciones_auxiliar": auxiliar,
        "total_asignaciones": len(asignaciones)
    }

async def obtener_resumen_aula(db: AsyncSession, aula_id: int) -> dict:
    """Obtiene el resumen completo de asignaciones de un aula"""
    aula = await db.get(Aula, aula_id)
    if not aula:
        raise HTTPException(status_code=404, detail="Aula no encontrada.")
    
    asignaciones = await obtener_asignaciones_por_aula(db, aula_id)
    
    docentes = [a.to_card_response() for a in asignaciones if a.es_docente]
    tutor = next((a.to_card_response() for a in asignaciones if a.es_tutor), None)
    auxiliar = next((a.to_card_response() for a in asignaciones if a.es_auxiliar), None)
    
    return {
        "aula_id": aula_id,
        "aula_nombre": aula.nombre_completo,
        "grado": aula.grado,
        "seccion": aula.seccion,
        "anio_escolar": aula.anio_escolar,
        "docentes": docentes,
        "tutor": tutor,
        "auxiliar": auxiliar,
        "total_docentes": len(docentes)
    }