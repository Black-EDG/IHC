from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import date, datetime

from app.modules.aulas.models import Aula, TurnoAula
from app.modules.aulas.schemas import (
    AulaCreate, 
    AulaUpdate,
    CrearAulasPorGradoRequest,
    AulaEstadisticasResponse
)
from app.modules.alumnos.models import Alumno, EstadoAlumno

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════

async def obtener_aula_por_id(db: AsyncSession, aula_id: int) -> Optional[Aula]:
    """Busca aula por ID con todas sus relaciones precargadas"""
    resultado = await db.execute(
        select(Aula)
        .options(
            selectinload(Aula.alumnos),
            selectinload(Aula.asignaciones),
            selectinload(Aula.asistencias)
        )
        .where(Aula.id == aula_id)
    )
    return resultado.scalars().first()

async def obtener_aula_por_grado_seccion(
    db: AsyncSession, 
    grado: int, 
    seccion: str, 
    anio_escolar: int
) -> Optional[Aula]:
    """Busca un aula específica por grado, sección y año"""
    resultado = await db.execute(
        select(Aula)
        .options(selectinload(Aula.alumnos))
        .where(
            and_(
                Aula.grado == grado,
                Aula.seccion == seccion.upper(),
                Aula.anio_escolar == anio_escolar
            )
        )
    )
    return resultado.scalars().first()

async def obtener_todas_las_aulas(
    db: AsyncSession,
    anio_escolar: Optional[int] = None,
    grado: Optional[int] = None,
    turno: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Aula]:
    """
    Lista todas las aulas con filtros opcionales.
    """
    query = select(Aula).options(
        selectinload(Aula.alumnos),
        selectinload(Aula.asignaciones)
    )
    
    if anio_escolar:
        query = query.where(Aula.anio_escolar == anio_escolar)
    
    if grado:
        query = query.where(Aula.grado == grado)
    
    if turno:
        query = query.where(Aula.turno == turno)
    
    query = query.order_by(
        Aula.anio_escolar.desc(),
        Aula.grado,
        Aula.seccion
    ).offset(skip).limit(limit)
    
    resultado = await db.execute(query)
    return resultado.scalars().all()

async def obtener_aulas_por_anio(db: AsyncSession, anio_escolar: int) -> List[Aula]:
    """Obtiene todas las aulas de un año escolar específico"""
    resultado = await db.execute(
        select(Aula)
        .options(selectinload(Aula.alumnos))
        .where(Aula.anio_escolar == anio_escolar)
        .order_by(Aula.grado, Aula.seccion)
    )
    return resultado.scalars().all()

async def obtener_aulas_por_grado(
    db: AsyncSession, 
    grado: int, 
    anio_escolar: Optional[int] = None
) -> List[Aula]:
    """Obtiene todas las secciones de un grado específico"""
    query = select(Aula).options(selectinload(Aula.alumnos)).where(Aula.grado == grado)
    
    if anio_escolar:
        query = query.where(Aula.anio_escolar == anio_escolar)
    else:
        # Si no se especifica año, traer el más reciente
        query = query.order_by(Aula.anio_escolar.desc())
    
    query = query.order_by(Aula.seccion)
    resultado = await db.execute(query)
    return resultado.scalars().all()

# ═══════════════════════════════════════════════════════════════
# OPERACIONES CRUD
# ═══════════════════════════════════════════════════════════════

async def crear_aula(db: AsyncSession, aula_data: AulaCreate) -> Aula:
    """
    Crea una nueva aula con validaciones completas.
    """
    # Validar que no exista la misma combinación
    existente = await obtener_aula_por_grado_seccion(
        db, 
        grado=aula_data.grado, 
        seccion=aula_data.seccion, 
        anio_escolar=aula_data.anio_escolar
    )
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El aula {aula_data.grado}° {aula_data.seccion} ya existe "
                    f"para el año escolar {aula_data.anio_escolar}."
        )
    
    datos = aula_data.model_dump()
    datos['seccion'] = datos['seccion'].upper()
    nueva_aula = Aula(**datos)
    
    db.add(nueva_aula)
    await db.commit()
    await db.refresh(nueva_aula)
    
    return nueva_aula

async def crear_aulas_por_grado(
    db: AsyncSession, 
    data: CrearAulasPorGradoRequest
) -> dict:
    """
    Crea múltiples secciones para un grado específico.
    
    Ejemplo: Crear 1° A, 1° B, 1° C, 1° D, 1° E para el año 2026
    """
    aulas_creadas = []
    errores = []
    
    for seccion in data.secciones:
        try:
            # Verificar si ya existe
            existente = await obtener_aula_por_grado_seccion(
                db,
                grado=data.grado,
                seccion=seccion,
                anio_escolar=data.anio_escolar
            )
            
            if existente:
                errores.append(
                    f"Aula {data.grado}° {seccion} ya existe para {data.anio_escolar}"
                )
                continue
            
            aula = Aula(
                grado=data.grado,
                seccion=seccion,
                anio_escolar=data.anio_escolar,
                turno=data.turno
            )
            db.add(aula)
            aulas_creadas.append(f"{data.grado}° {seccion}")
            
        except Exception as e:
            errores.append(f"Error creando {data.grado}° {seccion}: {str(e)}")
    
    await db.commit()
    
    return {
        "grado": data.grado,
        "anio_escolar": data.anio_escolar,
        "aulas_creadas": len(aulas_creadas),
        "secciones_creadas": aulas_creadas,
        "errores": errores
    }

async def actualizar_aula(
    db: AsyncSession, 
    aula_id: int, 
    aula_data: AulaUpdate
) -> Optional[Aula]:
    """
    Actualiza los datos de un aula.
    Solo se permite cambiar el turno (grado, sección y año son inmutables).
    """
    aula = await obtener_aula_por_id(db, aula_id)
    
    if not aula:
        return None
    
    update_data = aula_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if hasattr(aula, key):
            setattr(aula, key, value)
    
    await db.commit()
    await db.refresh(aula)
    return aula

async def eliminar_aula(db: AsyncSession, aula_id: int) -> bool:
    """
    Elimina un aula solo si no tiene alumnos ni asignaciones activas.
    """
    aula = await obtener_aula_por_id(db, aula_id)
    
    if not aula:
        return False
    
    # Verificar alumnos
    if aula.alumnos:
        alumnos_activos = [a for a in aula.alumnos if a.estado == EstadoAlumno.MATRICULADO]
        if alumnos_activos:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede eliminar el aula {aula.nombre_corto} porque tiene "
                        f"{len(alumnos_activos)} alumnos matriculados. "
                        "Traslade o retire a los alumnos primero."
            )
    
    # Verificar asignaciones
    if aula.asignaciones:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar el aula {aula.nombre_corto} porque tiene "
                    f"{len(aula.asignaciones)} docentes/asignaciones vinculadas."
        )
    
    await db.delete(aula)
    await db.commit()
    return True

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE NEGOCIO
# ═══════════════════════════════════════════════════════════════

async def obtener_listado_aula(db: AsyncSession, aula_id: int) -> dict:
    """
    Obtiene el listado completo de un aula con sus alumnos.
    """
    aula = await obtener_aula_por_id(db, aula_id)
    
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula con ID {aula_id} no encontrada."
        )
    
    return {
        "aula": aula.to_card_response(),
        "total_alumnos": aula.cantidad_alumnos,
        "alumnos": aula.listado_alumnos(solo_activos=True)
    }

async def obtener_asistencia_aula_fecha(
    db: AsyncSession, 
    aula_id: int, 
    fecha: Optional[date] = None
) -> dict:
    """
    Obtiene el resumen de asistencia de un aula en una fecha específica.
    """
    aula = await obtener_aula_por_id(db, aula_id)
    
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula con ID {aula_id} no encontrada."
        )
    
    return aula.resumen_asistencias_fecha(fecha)

async def proceso_crear_aulas_siguiente_anio(
    db: AsyncSession, 
    anio_actual: int,
    secciones_por_defecto: List[str] = ['A', 'B', 'C', 'D', 'E']
) -> dict:
    """
    Crea automáticamente las aulas para el siguiente año escolar.
    
    Copia la estructura del año actual:
    - Mismas secciones por grado
    - Mismo turno
    
    Este proceso se ejecuta al finalizar el año escolar para preparar
    la estructura del siguiente año.
    """
    anio_siguiente = anio_actual + 1
    aulas_actuales = await obtener_aulas_por_anio(db, anio_actual)
    
    if not aulas_actuales:
        # Si no hay aulas en el año actual, crear estructura por defecto
        aulas_creadas = 0
        errores = []
        
        for grado in range(1, 6):
            for seccion in secciones_por_defecto:
                try:
                    existente = await obtener_aula_por_grado_seccion(
                        db, grado=grado, seccion=seccion, anio_escolar=anio_siguiente
                    )
                    if not existente:
                        aula = Aula(
                            grado=grado,
                            seccion=seccion,
                            anio_escolar=anio_siguiente,
                            turno='mañana'
                        )
                        db.add(aula)
                        aulas_creadas += 1
                except Exception as e:
                    errores.append(f"Error: {str(e)}")
        
        await db.commit()
        
        return {
            "anio_origen": anio_actual,
            "anio_destino": anio_siguiente,
            "aulas_creadas": aulas_creadas,
            "secciones_por_grado": {
                str(g): secciones_por_defecto for g in range(1, 6)
            },
            "errores": errores,
            "fecha_proceso": datetime.now(),
            "metodo": "estructura_por_defecto"
        }
    
    # Si hay aulas en el año actual, replicar estructura
    aulas_creadas = 0
    secciones_por_grado = {}
    errores = []
    
    # Agrupar secciones por grado del año actual
    for aula in aulas_actuales:
        if aula.grado not in secciones_por_grado:
            secciones_por_grado[aula.grado] = set()
        secciones_por_grado[aula.grado].add(aula.seccion)
    
    # Crear aulas para el siguiente año
    for grado, secciones in secciones_por_grado.items():
        for seccion in secciones:
            try:
                # Verificar si ya existe
                existente = await obtener_aula_por_grado_seccion(
                    db, grado=grado, seccion=seccion, anio_escolar=anio_siguiente
                )
                
                if existente:
                    continue
                
                # Obtener el turno del aula actual
                aula_actual = next(
                    (a for a in aulas_actuales 
                     if a.grado == grado and a.seccion == seccion), 
                    None
                )
                turno = aula_actual.turno if aula_actual else 'mañana'
                
                nueva_aula = Aula(
                    grado=grado,
                    seccion=seccion,
                    anio_escolar=anio_siguiente,
                    turno=turno
                )
                db.add(nueva_aula)
                aulas_creadas += 1
                
            except Exception as e:
                errores.append(f"Error {grado}° {seccion}: {str(e)}")
    
    await db.commit()
    
    return {
        "anio_origen": anio_actual,
        "anio_destino": anio_siguiente,
        "aulas_creadas": aulas_creadas,
        "secciones_por_grado": {
            str(g): sorted(list(s)) for g, s in secciones_por_grado.items()
        },
        "errores": errores,
        "fecha_proceso": datetime.now(),
        "metodo": "replica_estructura_actual"
    }

async def obtener_estadisticas_aula(db: AsyncSession, aula_id: int) -> AulaEstadisticasResponse:
    """
    Obtiene estadísticas detalladas de un aula para el dashboard.
    """
    aula = await obtener_aula_por_id(db, aula_id)
    
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula con ID {aula_id} no encontrada."
        )
    
    # Alumnos suspendidos actualmente
    suspendidos = sum(1 for a in aula.alumnos if a.esta_suspendido)
    
    # Alumnos en riesgo de inhabilitación (>30% faltas)
    riesgo = sum(
        1 for a in aula.alumnos 
        if a.resumen_asistencias().get('riesgo_inhabilitacion', False)
    )
    
    # Calcular promedio de asistencia semanal (última semana)
    # Esto es una aproximación, en producción se calcularía con datos reales
    promedio_asistencia = 0.0
    if aula.alumnos:
        promedios = [
            a.resumen_asistencias().get('porcentaje_asistencia', 0)
            for a in aula.alumnos
            if a.esta_matriculado
        ]
        promedio_asistencia = round(sum(promedios) / len(promedios), 1) if promedios else 0.0
    
    return AulaEstadisticasResponse(
        aula=aula.to_card_response(),
        alumnos_matriculados=aula.cantidad_alumnos,
        alumnos_suspendidos=suspendidos,
        alumnos_riesgo_inhabilitacion=riesgo,
        promedio_asistencia_semanal=promedio_asistencia,
        docentes_count=len(aula.docentes_asignados),
        tiene_tutor=aula.tiene_tutor,
        tiene_auxiliar=aula.tiene_auxiliar
    )

async def obtener_estadisticas_por_grado(db: AsyncSession, anio_escolar: int) -> dict:
    """
    Obtiene estadísticas agrupadas por grado para un año escolar.
    """
    aulas = await obtener_aulas_por_anio(db, anio_escolar)
    
    estadisticas = {}
    for grado in range(1, 6):
        aulas_grado = [a for a in aulas if a.grado == grado]
        total_alumnos = sum(a.cantidad_alumnos for a in aulas_grado)
        total_secciones = len(aulas_grado)
        
        estadisticas[f"{grado}°"] = {
            "secciones": total_secciones,
            "total_alumnos": total_alumnos,
            "promedio_alumnos_por_seccion": round(
                total_alumnos / total_secciones, 1
            ) if total_secciones > 0 else 0
        }
    
    return {
        "anio_escolar": anio_escolar,
        "total_aulas": len(aulas),
        "total_alumnos": sum(a.cantidad_alumnos for a in aulas),
        "por_grado": estadisticas
    }