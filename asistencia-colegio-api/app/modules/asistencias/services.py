from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func, or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.modules.asistencias.models import Asistencia, EstadoAsistencia
from app.modules.asistencias.schemas import (
    AsistenciaIndividualCreate,
    AsistenciaMasivaCreate,
    AsistenciaUpdate
)
from app.modules.alumnos.models import Alumno, EstadoAlumno
from app.modules.aulas.models import Aula
from app.modules.usuarios.models import Usuario
from app.modules.cursos.models import Curso

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════

async def obtener_asistencia_por_id(db: AsyncSession, asistencia_id: int) -> Optional[Asistencia]:
    """Busca una asistencia por su ID con todas las relaciones"""
    resultado = await db.execute(
        select(Asistencia)
        .options(
            selectinload(Asistencia.alumno),
            selectinload(Asistencia.usuario),
            selectinload(Asistencia.curso),
            selectinload(Asistencia.aula),
            selectinload(Asistencia.justificacion)
        )
        .where(Asistencia.id == asistencia_id)
    )
    return resultado.scalars().first()

async def obtener_asistencia_alumno_fecha(
    db: AsyncSession,
    alumno_id: int,
    fecha: date,
    curso_id: Optional[int] = None
) -> Optional[Asistencia]:
    """Busca la asistencia de un alumno en una fecha específica (y curso opcional)"""
    condiciones = [
        Asistencia.alumno_id == alumno_id,
        Asistencia.fecha == fecha
    ]
    
    if curso_id is not None:
        condiciones.append(Asistencia.curso_id == curso_id)
    else:
        condiciones.append(Asistencia.curso_id.is_(None))
    
    resultado = await db.execute(
        select(Asistencia).where(and_(*condiciones))
    )
    return resultado.scalars().first()

async def obtener_asistencias_por_aula_fecha(
    db: AsyncSession,
    aula_id: int,
    fecha: date,
    curso_id: Optional[int] = None
) -> List[Asistencia]:
    """Obtiene todas las asistencias de un aula en una fecha"""
    condiciones = [
        Asistencia.aula_id == aula_id,
        Asistencia.fecha == fecha
    ]
    
    if curso_id is not None:
        condiciones.append(Asistencia.curso_id == curso_id)
    
    resultado = await db.execute(
        select(Asistencia)
        .options(
            selectinload(Asistencia.alumno),
            selectinload(Asistencia.usuario)
        )
        .where(and_(*condiciones))
        .order_by(Asistencia.alumno_id)
    )
    return resultado.scalars().all()

async def obtener_asistencias_por_alumno(
    db: AsyncSession,
    alumno_id: int,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    solo_faltas: bool = False
) -> List[Asistencia]:
    """Obtiene el historial de asistencias de un alumno en un período"""
    condiciones = [Asistencia.alumno_id == alumno_id]
    
    if fecha_inicio:
        condiciones.append(Asistencia.fecha >= fecha_inicio)
    if fecha_fin:
        condiciones.append(Asistencia.fecha <= fecha_fin)
    if solo_faltas:
        condiciones.append(
            Asistencia.estado.in_([EstadoAsistencia.AUSENTE, EstadoAsistencia.JUSTIFICADO])
        )
    
    resultado = await db.execute(
        select(Asistencia)
        .options(
            selectinload(Asistencia.curso),
            selectinload(Asistencia.usuario),
            selectinload(Asistencia.justificacion)
        )
        .where(and_(*condiciones))
        .order_by(Asistencia.fecha.desc())
    )
    return resultado.scalars().all()

# ═══════════════════════════════════════════════════════════════
# REGISTRO DE ASISTENCIAS
# ═══════════════════════════════════════════════════════════════

async def registrar_asistencia_individual(
    db: AsyncSession,
    usuario_id: int,
    data: AsistenciaIndividualCreate,
    curso_id: Optional[int] = None,
    aula_id: Optional[int] = None
) -> Asistencia:
    """
    Registra la asistencia de un solo alumno.
    Usado para correcciones rápidas o llegadas tarde.
    """
    
    # Validar alumno
    alumno = await db.get(Alumno, data.alumno_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")
    
    if not alumno.esta_matriculado:
        raise HTTPException(status_code=400, detail="El alumno no está matriculado.")
    
    if alumno.esta_suspendido:
        raise HTTPException(
            status_code=400,
            detail=f"El alumno {alumno.nombre_completo} está suspendido hasta {alumno.suspendido_hasta}."
        )
    
    # Si no se proporciona aula_id, usar el aula del alumno
    if not aula_id:
        aula_id = alumno.aula_id
    
    # Validar que no exista ya una asistencia para este alumno/fecha/curso
    fecha_hoy = date.today()
    existente = await obtener_asistencia_alumno_fecha(db, data.alumno_id, fecha_hoy, curso_id)
    if existente:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un registro de asistencia para este alumno en la fecha {fecha_hoy}."
        )
    
    nueva_asistencia = Asistencia(
        alumno_id=data.alumno_id,
        usuario_id=usuario_id,
        curso_id=curso_id,
        aula_id=aula_id,
        fecha=fecha_hoy,
        estado=data.estado,
        observacion=data.observacion
    )
    
    db.add(nueva_asistencia)
    await db.commit()
    await db.refresh(nueva_asistencia)
    
    return nueva_asistencia

async def registrar_asistencia_masiva(
    db: AsyncSession,
    usuario_id: int,
    data: AsistenciaMasivaCreate
) -> dict:
    """
    Registra la asistencia de todos los alumnos de un aula.
    
    Flujo:
    1. Auxiliar: curso_id=NULL → Asistencia General del día
    2. Docente: curso_id=5 → Asistencia de Matemática, Comunicación, etc.
    """
    
    # Validar aula
    aula = await db.get(Aula, data.aula_id)
    if not aula:
        raise HTTPException(status_code=404, detail="Aula no encontrada.")
    
    # Validar curso si es asistencia por curso
    if data.curso_id:
        curso = await db.get(Curso, data.curso_id)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado.")
    
    # Obtener alumnos activos del aula
    resultado = await db.execute(
        select(Alumno).where(
            and_(
                Alumno.aula_id == data.aula_id,
                Alumno.estado == EstadoAlumno.MATRICULADO
            )
        )
    )
    alumnos_activos = resultado.scalars().all()
    
    registros_creados = 0
    errores = []
    alumnos_procesados = []
    
    for asistencia_data in data.asistencias:
        try:
            # Verificar que el alumno pertenezca al aula
            alumno = next((a for a in alumnos_activos if a.id == asistencia_data.alumno_id), None)
            if not alumno:
                errores.append(f"Alumno ID {asistencia_data.alumno_id} no pertenece al aula {data.aula_id}")
                continue
            
            # Verificar suspensión
            if alumno.esta_suspendido:
                errores.append(f"Alumno {alumno.nombre_completo} está suspendido")
                continue
            
            # Verificar duplicado
            existente = await obtener_asistencia_alumno_fecha(
                db, asistencia_data.alumno_id, data.fecha, data.curso_id
            )
            if existente:
                errores.append(f"Ya existe asistencia para {alumno.nombre_completo}")
                continue
            
            # Crear registro
            nueva = Asistencia(
                alumno_id=asistencia_data.alumno_id,
                usuario_id=usuario_id,
                curso_id=data.curso_id,
                aula_id=data.aula_id,
                fecha=data.fecha,
                estado=asistencia_data.estado,
                observacion=asistencia_data.observacion
            )
            db.add(nueva)
            registros_creados += 1
            alumnos_procesados.append(alumno.nombre_completo)
            
        except Exception as e:
            errores.append(f"Error con alumno {asistencia_data.alumno_id}: {str(e)}")
    
    await db.commit()
    
    return {
        "aula": aula.nombre_completo,
        "fecha": data.fecha.isoformat(),
        "tipo": "General" if not data.curso_id else f"Curso ID {data.curso_id}",
        "total_alumnos": len(alumnos_activos),
        "registros_creados": registros_creados,
        "errores": errores,
        "alumnos_procesados": alumnos_procesados
    }

async def actualizar_asistencia(
    db: AsyncSession,
    asistencia_id: int,
    usuario_id: int,
    data: AsistenciaUpdate
) -> Optional[Asistencia]:
    """
    Actualiza el estado de una asistencia existente.
    Solo el Auxiliar puede modificar asistencias generales.
    """
    asistencia = await obtener_asistencia_por_id(db, asistencia_id)
    
    if not asistencia:
        return None
    
    # Solo el Auxiliar puede modificar asistencias generales
    usuario = await db.get(Usuario, usuario_id)
    if asistencia.es_asistencia_general and usuario.rol != 'auxiliar':
        raise HTTPException(
            status_code=403,
            detail="Solo el Auxiliar puede modificar la asistencia general del día."
        )
    
    asistencia.estado = data.estado
    if data.observacion is not None:
        asistencia.observacion = data.observacion
    
    await db.commit()
    await db.refresh(asistencia)
    return asistencia

# ═══════════════════════════════════════════════════════════════
# REPORTES Y ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════

async def obtener_resumen_aula_fecha(
    db: AsyncSession,
    aula_id: int,
    fecha: date,
    curso_id: Optional[int] = None
) -> dict:
    """Obtiene el resumen de asistencia de un aula en una fecha"""
    
    aula = await db.get(Aula, aula_id)
    if not aula:
        raise HTTPException(status_code=404, detail="Aula no encontrada.")
    
    # Obtener alumnos activos
    resultado = await db.execute(
        select(func.count()).where(
            and_(
                Alumno.aula_id == aula_id,
                Alumno.estado == EstadoAlumno.MATRICULADO
            )
        )
    )
    total_alumnos = resultado.scalar()
    
    # Obtener asistencias del día
    asistencias = await obtener_asistencias_por_aula_fecha(db, aula_id, fecha, curso_id)
    
    presentes = sum(1 for a in asistencias if a.estado == EstadoAsistencia.PRESENTE)
    ausentes = sum(1 for a in asistencias if a.estado == EstadoAsistencia.AUSENTE)
    tardes = sum(1 for a in asistencias if a.estado == EstadoAsistencia.TARDE)
    justificados = sum(1 for a in asistencias if a.estado == EstadoAsistencia.JUSTIFICADO)
    sin_registro = total_alumnos - len(asistencias)
    
    return {
        "aula_id": aula_id,
        "aula_nombre": aula.nombre_completo,
        "fecha": fecha,
        "total_alumnos": total_alumnos,
        "presentes": presentes,
        "ausentes": ausentes,
        "tardes": tardes,
        "justificados": justificados,
        "sin_registro": max(0, sin_registro),
        "porcentaje_asistencia": round((presentes / total_alumnos * 100) if total_alumnos > 0 else 0, 1)
    }

async def obtener_resumen_alumno_periodo(
    db: AsyncSession,
    alumno_id: int,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> dict:
    """Obtiene el resumen completo de asistencias de un alumno"""
    
    alumno = await db.get(Alumno, alumno_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")
    
    if not fecha_inicio:
        fecha_inicio = date(date.today().year, 1, 1)
    if not fecha_fin:
        fecha_fin = date.today()
    
    asistencias = await obtener_asistencias_por_alumno(db, alumno_id, fecha_inicio, fecha_fin)
    
    # Contar solo asistencias generales para el cálculo de inhabilitación
    asistencias_generales = [a for a in asistencias if a.es_asistencia_general]
    
    total = len(asistencias_generales)
    presentes = sum(1 for a in asistencias_generales if a.estado == EstadoAsistencia.PRESENTE)
    ausentes = sum(1 for a in asistencias_generales if a.estado == EstadoAsistencia.AUSENTE)
    tardes = sum(1 for a in asistencias_generales if a.estado == EstadoAsistencia.TARDE)
    justificados = sum(1 for a in asistencias_generales if a.estado == EstadoAsistencia.JUSTIFICADO)
    
    porcentaje = round((presentes / total * 100) if total > 0 else 0, 1)
    riesgo = ausentes > (total * 0.3) if total > 0 else False
    
    # Contar faltas consecutivas (para límite de justificaciones virtuales)
    faltas_consecutivas = 0
    for a in sorted(asistencias_generales, key=lambda x: x.fecha, reverse=True):
        if a.estado in [EstadoAsistencia.AUSENTE, EstadoAsistencia.JUSTIFICADO]:
            faltas_consecutivas += 1
        else:
            break
    
    justificaciones_virtuales_disponibles = max(0, 3 - faltas_consecutivas)
    
    return {
        "alumno_id": alumno_id,
        "alumno_nombre": alumno.nombre_completo,
        "grado_seccion": alumno.grado_seccion,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "total_registros": total,
        "presentes": presentes,
        "ausentes": ausentes,
        "tardes": tardes,
        "justificados": justificados,
        "porcentaje_asistencia": porcentaje,
        "riesgo_inhabilitacion": riesgo,
        "faltas_consecutivas": faltas_consecutivas,
        "justificaciones_virtuales_disponibles": justificaciones_virtuales_disponibles
    }

async def obtener_estadisticas_generales_hoy(db: AsyncSession) -> dict:
    """Estadísticas generales de asistencia del día actual"""
    
    hoy = date.today()
    
    # Total alumnos matriculados
    resultado = await db.execute(
        select(func.count()).where(Alumno.estado == EstadoAlumno.MATRICULADO)
    )
    total_matriculados = resultado.scalar()
    
    # Asistencias de hoy (solo generales)
    resultado = await db.execute(
        select(Asistencia).where(
            and_(
                Asistencia.fecha == hoy,
                Asistencia.curso_id.is_(None)
            )
        )
    )
    asistencias_hoy = resultado.scalars().all()
    
    presentes = sum(1 for a in asistencias_hoy if a.estado == EstadoAsistencia.PRESENTE)
    ausentes = sum(1 for a in asistencias_hoy if a.estado == EstadoAsistencia.AUSENTE)
    tardes = sum(1 for a in asistencias_hoy if a.estado == EstadoAsistencia.TARDE)
    justificados = sum(1 for a in asistencias_hoy if a.estado == EstadoAsistencia.JUSTIFICADO)
    
    # Alumnos en riesgo (>30% faltas)
    alumnos_riesgo = 0
    # Este cálculo es pesado, se puede optimizar con una vista materializada
    
    return {
        "fecha_consulta": hoy,
        "total_alumnos_matriculados": total_matriculados,
        "total_asistencias_hoy": len(asistencias_hoy),
        "presentes_hoy": presentes,
        "ausentes_hoy": ausentes,
        "tardes_hoy": tardes,
        "justificados_hoy": justificados,
        "porcentaje_asistencia_hoy": round(
            (presentes / total_matriculados * 100) if total_matriculados > 0 else 0, 1
        ),
        "alumnos_riesgo_inhabilitacion": alumnos_riesgo
    }