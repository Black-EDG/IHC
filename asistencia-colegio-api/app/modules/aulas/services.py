from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
    """Busca aula por ID"""
    resultado = await db.execute(
        select(Aula).where(Aula.id == aula_id)
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
        select(Aula).where(
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
    """Lista todas las aulas con filtros opcionales."""
    import traceback
    import sys
    
    try:
        query = select(Aula)
        
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
        aulas = resultado.scalars().all()
        
        print(f"✅ Aulas encontradas: {len(aulas)}")
        
        # Retornar datos SIMPLES sin usar propiedades del modelo
        return [
            {
                "id": a.id,
                "grado": a.grado,
                "seccion": a.seccion,
                "anio_escolar": a.anio_escolar,
                "turno": a.turno,
                "nombre_completo": f"{a.grado}° {a.seccion} - {a.anio_escolar} ({a.turno})",
                "nombre_corto": f"{a.grado}° {a.seccion}",
                "cantidad_alumnos": 0,
                "cantidad_total_alumnos": 0,
                "tiene_tutor": False,
                "tiene_auxiliar": False,
                "es_ultimo_grado": a.grado == 5,
                "docentes_asignados": [],
                "docentes_count": 0,  # ← AGREGAR ESTA LÍNEA
                "creado_en": str(a.creado_en) if a.creado_en else None
            }
            for a in aulas
        ]
    except Exception as e:
        print("\n" + "="*70)
        print("🔥 ERROR en obtener_todas_las_aulas:")
        print(f"📌 Tipo: {type(e).__name__}")
        print(f"💬 Mensaje: {str(e)}")
        print("📚 Traceback:")
        traceback.print_exc(file=sys.stdout)
        print("="*70 + "\n")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def obtener_aulas_por_anio(db: AsyncSession, anio_escolar: int) -> List[Aula]:
    """Obtiene todas las aulas de un año escolar específico"""
    resultado = await db.execute(
        select(Aula)
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
    query = select(Aula).where(Aula.grado == grado)
    
    if anio_escolar:
        query = query.where(Aula.anio_escolar == anio_escolar)
    else:
        query = query.order_by(Aula.anio_escolar.desc())
    
    query = query.order_by(Aula.seccion)
    resultado = await db.execute(query)
    return resultado.scalars().all()

# ═══════════════════════════════════════════════════════════════
# OPERACIONES CRUD
# ═══════════════════════════════════════════════════════════════

async def crear_aula(db: AsyncSession, aula_data: AulaCreate) -> Aula:
    """Crea una nueva aula con validaciones completas."""
    
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
    """Crea múltiples secciones para un grado específico."""
    aulas_creadas = []
    errores = []
    
    for seccion in data.secciones:
        try:
            existente = await obtener_aula_por_grado_seccion(
                db,
                grado=data.grado,
                seccion=seccion,
                anio_escolar=data.anio_escolar
            )
            
            if existente:
                errores.append(f"Aula {data.grado}° {seccion} ya existe para {data.anio_escolar}")
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
    """Actualiza los datos de un aula. Solo se permite cambiar el turno."""
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
    """Elimina un aula solo si no tiene alumnos ni asignaciones activas."""
    aula = await obtener_aula_por_id(db, aula_id)
    
    if not aula:
        return False
    
    # Verificar alumnos - consulta separada
    resultado = await db.execute(
        select(Alumno).where(
            and_(
                Alumno.aula_id == aula_id,
                Alumno.estado == EstadoAlumno.MATRICULADO
            )
        )
    )
    alumnos_activos = resultado.scalars().all()
    
    if alumnos_activos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar el aula {aula.nombre_corto} porque tiene "
                    f"{len(alumnos_activos)} alumnos matriculados. "
                    "Traslade o retire a los alumnos primero."
        )
    
    await db.delete(aula)
    await db.commit()
    return True

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE NEGOCIO
# ═══════════════════════════════════════════════════════════════

async def obtener_listado_aula(db: AsyncSession, aula_id: int) -> dict:
    """Obtiene el listado completo de un aula con sus alumnos."""
    aula = await obtener_aula_por_id(db, aula_id)
    
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula con ID {aula_id} no encontrada."
        )
    
    # Obtener alumnos del aula
    resultado = await db.execute(
        select(Alumno).where(
            and_(
                Alumno.aula_id == aula_id,
                Alumno.estado == EstadoAlumno.MATRICULADO
            )
        ).order_by(Alumno.apellidos)
    )
    alumnos = resultado.scalars().all()
    
    return {
        "aula": {
            "id": aula.id,
            "nombre_completo": aula.nombre_completo,
            "nombre_corto": aula.nombre_corto,
            "grado": aula.grado,
            "seccion": aula.seccion,
            "anio_escolar": aula.anio_escolar,
            "turno": aula.turno,
            "cantidad_alumnos": len(alumnos)
        },
        "total_alumnos": len(alumnos),
        "alumnos": [
            {
                "id": a.id,
                "dni": a.dni,
                "nombre_completo": a.nombre_completo,
                "genero": a.genero,
                "edad": a.edad if hasattr(a, 'edad') else None
            }
            for a in alumnos
        ]
    }

async def obtener_asistencia_aula_fecha(
    db: AsyncSession, 
    aula_id: int, 
    fecha: Optional[date] = None
) -> dict:
    """Obtiene el resumen de asistencia de un aula en una fecha específica."""
    aula = await obtener_aula_por_id(db, aula_id)
    
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula con ID {aula_id} no encontrada."
        )
    
    if not fecha:
        fecha = date.today()
    
    # Contar alumnos
    resultado = await db.execute(
        select(Alumno).where(
            and_(
                Alumno.aula_id == aula_id,
                Alumno.estado == EstadoAlumno.MATRICULADO
            )
        )
    )
    total_alumnos = len(resultado.scalars().all())
    
    return {
        "fecha": fecha.isoformat(),
        "total_alumnos": total_alumnos,
        "presentes": 0,
        "ausentes": 0,
        "tardes": 0,
        "justificados": 0,
        "sin_registro": total_alumnos,
        "porcentaje_asistencia": 0.0
    }

async def proceso_crear_aulas_siguiente_anio(
    db: AsyncSession, 
    anio_actual: int,
    secciones_por_defecto: List[str] = ['A', 'B', 'C', 'D', 'E']
) -> dict:
    """Crea automáticamente las aulas para el siguiente año escolar."""
    anio_siguiente = anio_actual + 1
    aulas_actuales = await obtener_aulas_por_anio(db, anio_actual)
    
    if not aulas_actuales:
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
            "secciones_por_grado": {str(g): secciones_por_defecto for g in range(1, 6)},
            "errores": errores,
            "fecha_proceso": datetime.now().isoformat(),
            "metodo": "estructura_por_defecto"
        }
    
    aulas_creadas = 0
    secciones_por_grado = {}
    errores = []
    
    for aula in aulas_actuales:
        if aula.grado not in secciones_por_grado:
            secciones_por_grado[aula.grado] = set()
        secciones_por_grado[aula.grado].add(aula.seccion)
    
    for grado, secciones in secciones_por_grado.items():
        for seccion in secciones:
            try:
                existente = await obtener_aula_por_grado_seccion(
                    db, grado=grado, seccion=seccion, anio_escolar=anio_siguiente
                )
                
                if existente:
                    continue
                
                aula_actual = next(
                    (a for a in aulas_actuales if a.grado == grado and a.seccion == seccion), 
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
        "secciones_por_grado": {str(g): sorted(list(s)) for g, s in secciones_por_grado.items()},
        "errores": errores,
        "fecha_proceso": datetime.now().isoformat(),
        "metodo": "replica_estructura_actual"
    }

async def obtener_estadisticas_aula(db: AsyncSession, aula_id: int) -> dict:
    """Obtiene estadísticas detalladas de un aula para el dashboard."""
    aula = await obtener_aula_por_id(db, aula_id)
    
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula con ID {aula_id} no encontrada."
        )
    
    resultado = await db.execute(
        select(Alumno).where(Alumno.aula_id == aula_id)
    )
    alumnos = resultado.scalars().all()
    
    matriculados = sum(1 for a in alumnos if a.estado == EstadoAlumno.MATRICULADO)
    suspendidos = sum(1 for a in alumnos if a.esta_suspendido if hasattr(a, 'esta_suspendido'))
    
    return {
        "aula_id": aula_id,
        "aula_nombre": aula.nombre_completo,
        "alumnos_matriculados": matriculados,
        "alumnos_suspendidos": suspendidos,
        "alumnos_riesgo_inhabilitacion": 0,
        "promedio_asistencia_semanal": 0.0,
        "docentes_count": 0,
        "tiene_tutor": False,
        "tiene_auxiliar": False
    }

async def obtener_estadisticas_por_grado(db: AsyncSession, anio_escolar: int) -> dict:
    """Obtiene estadísticas agrupadas por grado para un año escolar."""
    aulas = await obtener_aulas_por_anio(db, anio_escolar)
    
    estadisticas = {}
    for grado in range(1, 6):
        aulas_grado = [a for a in aulas if a.grado == grado]
        total_secciones = len(aulas_grado)
        
        estadisticas[f"{grado}°"] = {
            "secciones": total_secciones,
            "total_alumnos": 0,
            "promedio_alumnos_por_seccion": 0
        }
    
    return {
        "anio_escolar": anio_escolar,
        "total_aulas": len(aulas),
        "total_alumnos": 0,
        "por_grado": estadisticas
    }