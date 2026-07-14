from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
# OPERACIONES DE BÚSQUEDA (SIN selectinload)
# ═══════════════════════════════════════════════════════════════

async def _enriquecer_asignacion(db: AsyncSession, asignacion: AsignacionAula) -> dict:
    """Convierte una asignación en diccionario con datos de relaciones"""
    usuario = await db.get(Usuario, asignacion.usuario_id)
    aula = await db.get(Aula, asignacion.aula_id)
    curso = await db.get(Curso, asignacion.curso_id) if asignacion.curso_id else None
    
    tipo_legible = {
        'docente_curso': 'Docente de Curso',
        'tutor_seccion': 'Tutor de Sección',
        'auxiliar_grado': 'Auxiliar de Grado'
    }
    
    return {
        "id": asignacion.id,
        "usuario_id": asignacion.usuario_id,
        "usuario_nombre": usuario.nombre_completo if usuario else "Desconocido",
        "usuario_dni": usuario.dni if usuario else None,
        "aula_id": asignacion.aula_id,
        "aula_nombre": aula.nombre_corto if aula else f"Aula {asignacion.aula_id}",
        "aula_completa": aula.nombre_completo if aula else None,
        "curso_id": asignacion.curso_id,
        "curso_nombre": curso.nombre if curso else None,
        "tipo_cargo": asignacion.tipo_cargo.value if hasattr(asignacion.tipo_cargo, 'value') else str(asignacion.tipo_cargo),
        "tipo_cargo_legible": tipo_legible.get(str(asignacion.tipo_cargo), str(asignacion.tipo_cargo)),
        "puede_pasar_asistencia": str(asignacion.tipo_cargo) in ['docente_curso', 'auxiliar_grado'],
        "grado": aula.grado if aula else None,
        "anio_escolar": aula.anio_escolar if aula else None,
        "nombre_completo_asignacion": f"{usuario.nombre_completo if usuario else '?'} → {curso.nombre if curso else 'General'} en {aula.nombre_corto if aula else '?'}",
        "creado_en": asignacion.creado_en.isoformat() if asignacion.creado_en else None
    }

async def obtener_asignacion_por_id(db: AsyncSession, asignacion_id: int) -> Optional[dict]:
    """Busca una asignación por ID"""
    resultado = await db.execute(
        select(AsignacionAula).where(AsignacionAula.id == asignacion_id)
    )
    asignacion = resultado.scalars().first()
    
    if not asignacion:
        return None
    
    return await _enriquecer_asignacion(db, asignacion)

async def obtener_asignaciones_por_usuario(
    db: AsyncSession, 
    usuario_id: int,
    tipo_cargo: Optional[str] = None,
    anio_escolar: Optional[int] = None
) -> List[dict]:
    """Obtiene todas las asignaciones de un usuario."""
    query = select(AsignacionAula).where(AsignacionAula.usuario_id == usuario_id)
    
    if tipo_cargo:
        query = query.where(AsignacionAula.tipo_cargo == tipo_cargo)
    
    if anio_escolar:
        # Subconsulta para filtrar por año escolar sin join problemático
        aulas_ids = await db.execute(
            select(Aula.id).where(Aula.anio_escolar == anio_escolar)
        )
        ids = [a[0] for a in aulas_ids.all()]
        if ids:
            query = query.where(AsignacionAula.aula_id.in_(ids))
        else:
            return []
    
    query = query.order_by(AsignacionAula.tipo_cargo)
    
    resultado = await db.execute(query)
    asignaciones = resultado.scalars().all()
    
    # Enriquecer cada asignación
    return [await _enriquecer_asignacion(db, a) for a in asignaciones]

async def obtener_asignaciones_por_aula(db: AsyncSession, aula_id: int) -> List[dict]:
    """Obtiene todas las asignaciones de un aula específica"""
    resultado = await db.execute(
        select(AsignacionAula)
        .where(AsignacionAula.aula_id == aula_id)
        .order_by(AsignacionAula.tipo_cargo)
    )
    asignaciones = resultado.scalars().all()
    
    return [await _enriquecer_asignacion(db, a) for a in asignaciones]

async def obtener_todas_las_asignaciones(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    anio_escolar: Optional[int] = None,
    tipo_cargo: Optional[str] = None
) -> List[dict]:
    """Lista todas las asignaciones con filtros"""
    query = select(AsignacionAula)
    
    if tipo_cargo:
        query = query.where(AsignacionAula.tipo_cargo == tipo_cargo)
    
    if anio_escolar:
        # Filtrar por año escolar sin join
        aulas_ids = await db.execute(
            select(Aula.id).where(Aula.anio_escolar == anio_escolar)
        )
        ids = [a[0] for a in aulas_ids.all()]
        if ids:
            query = query.where(AsignacionAula.aula_id.in_(ids))
        else:
            return []
    
    query = query.offset(skip).limit(limit)
    
    resultado = await db.execute(query)
    asignaciones = resultado.scalars().all()
    
    return [await _enriquecer_asignacion(db, a) for a in asignaciones]

# ═══════════════════════════════════════════════════════════════
# OPERACIONES CRUD
# ═══════════════════════════════════════════════════════════════

async def crear_asignacion(db: AsyncSession, data: AsignacionCreate) -> dict:
    """Crea una nueva asignación con todas las validaciones de negocio."""
    
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
        
        if usuario.rol not in [RolUsuario.docente, RolUsuario.admin]:
            raise HTTPException(
                status_code=400,
                detail=f"El usuario {usuario.nombre_completo} es {usuario.rol.value}. Solo los docentes pueden dictar cursos."
            )
    
    # Validar que un tutor sea docente
    if data.tipo_cargo == TipoResponsabilidad.TUTOR_SECCION:
        if usuario.rol not in [RolUsuario.docente, RolUsuario.admin]:
            raise HTTPException(status_code=400, detail="Solo los docentes pueden ser tutores de sección.")
        
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
            raise HTTPException(status_code=400, detail="Solo los auxiliares pueden ser asignados como auxiliar de grado.")
    
    # Verificar duplicado
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
    
    return await _enriquecer_asignacion(db, nueva_asignacion)

async def crear_asignacion_masiva(db: AsyncSession, data: AsignacionMasivaRequest) -> dict:
    """Asigna un docente a múltiples aulas para un mismo curso."""
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
                "id": asignacion["id"],
                "aula": asignacion["aula_nombre"]
            })
        except HTTPException as e:
            errores.append({"aula_id": aula_id, "error": e.detail})
    
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
) -> Optional[dict]:
    """Actualiza los datos de una asignación existente"""
    resultado = await db.execute(
        select(AsignacionAula).where(AsignacionAula.id == asignacion_id)
    )
    asignacion = resultado.scalars().first()
    
    if not asignacion:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if hasattr(asignacion, key):
            setattr(asignacion, key, value)
    
    await db.commit()
    await db.refresh(asignacion)
    
    return await _enriquecer_asignacion(db, asignacion)

async def eliminar_asignacion(db: AsyncSession, asignacion_id: int) -> bool:
    """Elimina una asignación"""
    resultado = await db.execute(
        select(AsignacionAula).where(AsignacionAula.id == asignacion_id)
    )
    asignacion = resultado.scalars().first()
    
    if not asignacion:
        return False
    
    await db.delete(asignacion)
    await db.commit()
    return True

# ═══════════════════════════════════════════════════════════════
# DASHBOARD Y REPORTES
# ═══════════════════════════════════════════════════════════════

async def obtener_dashboard_docente(db: AsyncSession, usuario_id: int) -> dict:
    """Obtiene el dashboard completo de un docente al iniciar sesión."""
    usuario = await db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    asignaciones = await obtener_asignaciones_por_usuario(db, usuario_id)
    
    docente = [a for a in asignaciones if a["tipo_cargo"] == "docente_curso"]
    tutor = [a for a in asignaciones if a["tipo_cargo"] == "tutor_seccion"]
    auxiliar = [a for a in asignaciones if a["tipo_cargo"] == "auxiliar_grado"]
    
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
    
    docentes = [a for a in asignaciones if a["tipo_cargo"] == "docente_curso"]
    tutor = next((a for a in asignaciones if a["tipo_cargo"] == "tutor_seccion"), None)
    auxiliar = next((a for a in asignaciones if a["tipo_cargo"] == "auxiliar_grado"), None)
    
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