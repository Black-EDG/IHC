from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func, desc
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import date, timedelta

from app.modules.justificaciones.models import Justificacion, EstadoTramiteJustificacion
from app.modules.justificaciones.schemas import (
    JustificacionCreate,
    JustificacionUpdateAuxiliar
)
from app.modules.asistencias.models import Asistencia, EstadoAsistencia
from app.modules.alumnos.models import Alumno, EstadoAlumno

# ═══════════════════════════════════════════════════════════════
# CONSTANTES DE NEGOCIO
# ═══════════════════════════════════════════════════════════════

MAX_JUSTIFICACIONES_VIRTUALES_CONSECUTIVAS = 3
"""
Límite de justificaciones virtuales consecutivas.
A la 4ta falta consecutiva, se bloquea la opción virtual y 
se obliga al padre a realizar el trámite de forma presencial.
"""

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════

async def obtener_justificacion_por_id(db: AsyncSession, justificacion_id: int) -> Optional[Justificacion]:
    """Busca una justificación por ID con la asistencia relacionada"""
    resultado = await db.execute(
        select(Justificacion)
        .options(
            selectinload(Justificacion.asistencia)
            .selectinload(Asistencia.alumno),
            selectinload(Justificacion.asistencia)
            .selectinload(Asistencia.aula)
        )
        .where(Justificacion.id == justificacion_id)
    )
    return resultado.scalars().first()

async def obtener_justificacion_por_asistencia(db: AsyncSession, asistencia_id: int) -> Optional[Justificacion]:
    """Busca si una falta ya tiene una justificación registrada"""
    resultado = await db.execute(
        select(Justificacion)
        .where(Justificacion.asistencia_id == asistencia_id)
    )
    return resultado.scalars().first()

async def obtener_todas_las_justificaciones(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    alumno_id: Optional[int] = None
) -> List[Justificacion]:
    """Lista todas las justificaciones con filtros"""
    query = select(Justificacion).options(
        selectinload(Justificacion.asistencia)
        .selectinload(Asistencia.alumno),
        selectinload(Justificacion.asistencia)
        .selectinload(Asistencia.aula)
    )
    
    if estado:
        query = query.where(Justificacion.estado == estado)
    
    if alumno_id:
        query = query.join(Asistencia).where(Asistencia.alumno_id == alumno_id)
    
    query = query.order_by(desc(Justificacion.creado_en)).offset(skip).limit(limit)
    
    resultado = await db.execute(query)
    return resultado.scalars().all()

async def obtener_justificaciones_por_alumno(
    db: AsyncSession,
    alumno_id: int
) -> List[Justificacion]:
    """Obtiene todas las justificaciones de un alumno"""
    resultado = await db.execute(
        select(Justificacion)
        .options(
            selectinload(Justificacion.asistencia)
            .selectinload(Asistencia.alumno),
            selectinload(Justificacion.asistencia)
            .selectinload(Asistencia.aula)
        )
        .join(Asistencia)
        .where(Asistencia.alumno_id == alumno_id)
        .order_by(desc(Justificacion.creado_en))
    )
    return resultado.scalars().all()

async def obtener_justificaciones_pendientes(db: AsyncSession) -> List[Justificacion]:
    """Obtiene todas las justificaciones pendientes de revisión"""
    resultado = await db.execute(
        select(Justificacion)
        .options(
            selectinload(Justificacion.asistencia)
            .selectinload(Asistencia.alumno),
            selectinload(Justificacion.asistencia)
            .selectinload(Asistencia.aula)
        )
        .where(Justificacion.estado == EstadoTramiteJustificacion.PENDIENTE)
        .order_by(Justificacion.creado_en)
    )
    return resultado.scalars().all()

# ═══════════════════════════════════════════════════════════════
# LÓGICA DE NEGOCIO: VERIFICACIÓN DE JUSTIFICACIONES VIRTUALES
# ═══════════════════════════════════════════════════════════════

async def verificar_justificaciones_virtuales_disponibles(
    db: AsyncSession,
    alumno_id: int
) -> dict:
    """
    Verifica si un alumno puede seguir justificando virtualmente.
    
    Regla de negocio:
    - Máximo 3 justificaciones virtuales consecutivas
    - A la 4ta falta consecutiva, se bloquea la opción virtual
    - El padre debe ir presencialmente al colegio
    
    Retorna:
    - faltas_consecutivas: cuántas faltas consecutivas tiene
    - justificaciones_virtuales_usadas: cuántas justificaciones virtuales ha usado
    - justificaciones_virtuales_disponibles: cuántas le quedan
    - puede_justificar_virtualmente: True/False
    """
    
    alumno = await db.get(Alumno, alumno_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")
    
    # Obtener todas las faltas del alumno ordenadas por fecha descendente
    resultado = await db.execute(
        select(Asistencia)
        .where(
            and_(
                Asistencia.alumno_id == alumno_id,
                Asistencia.curso_id.is_(None),  # Solo asistencias generales
                Asistencia.estado.in_([
                    EstadoAsistencia.AUSENTE,
                    EstadoAsistencia.JUSTIFICADO
                ])
            )
        )
        .order_by(desc(Asistencia.fecha))
    )
    faltas = resultado.scalars().all()
    
    # Contar faltas consecutivas (hacia atrás desde la más reciente)
    faltas_consecutivas = 0
    justificaciones_virtuales_usadas = 0
    
    if faltas:
        # Verificar que la falta más reciente sea consecutiva con hoy o ayer
        fecha_referencia = date.today()
        
        for falta in faltas:
            # Verificar si es consecutiva (diferencia de 1 día o menos)
            if faltas_consecutivas == 0:
                # La primera falta debe ser reciente (hoy, ayer o anteayer)
                diferencia = (fecha_referencia - falta.fecha).days
                if diferencia <= faltas_consecutivas + 2:
                    faltas_consecutivas += 1
                    if falta.estado == EstadoAsistencia.JUSTIFICADO:
                        justificaciones_virtuales_usadas += 1
                else:
                    break
            else:
                # Verificar que sea consecutiva con la anterior
                if faltas[faltas_consecutivas - 1].fecha - falta.fecha <= timedelta(days=1):
                    faltas_consecutivas += 1
                    if falta.estado == EstadoAsistencia.JUSTIFICADO:
                        justificaciones_virtuales_usadas += 1
                else:
                    break
    
    justificaciones_disponibles = max(0, MAX_JUSTIFICACIONES_VIRTUALES_CONSECUTIVAS - justificaciones_virtuales_usadas)
    puede_justificar = justificaciones_disponibles > 0
    
    # Mensaje claro para el padre
    if puede_justificar:
        mensaje = f"Puede justificar virtualmente. Le quedan {justificaciones_disponibles} justificación(es) virtual(es)."
    else:
        mensaje = (
            f"Ha alcanzado el límite de {MAX_JUSTIFICACIONES_VIRTUALES_CONSECUTIVAS} justificaciones virtuales consecutivas. "
            "Debe acercarse presencialmente a la Dirección del colegio para justificar esta falta."
        )
    
    return {
        "alumno_id": alumno_id,
        "alumno_nombre": alumno.nombre_completo,
        "faltas_consecutivas": faltas_consecutivas,
        "justificaciones_virtuales_usadas": justificaciones_virtuales_usadas,
        "justificaciones_virtuales_disponibles": justificaciones_disponibles,
        "puede_justificar_virtualmente": puede_justificar,
        "mensaje": mensaje
    }

# ═══════════════════════════════════════════════════════════════
# OPERACIONES CRUD
# ═══════════════════════════════════════════════════════════════

async def crear_justificacion(
    db: AsyncSession,
    data: JustificacionCreate,
    alumno_id: int  # Viene del contexto del padre logueado
) -> Justificacion:
    """
    Crea una nueva justificación desde la App Familiar.
    
    Flujo:
    1. Verificar que la asistencia exista y sea una falta
    2. Verificar que la falta pertenezca al alumno correcto
    3. Verificar límite de justificaciones virtuales consecutivas
    4. Verificar que no exista ya una justificación para esta falta
    5. Crear la justificación en estado 'pendiente'
    """
    
    # 1. Obtener la asistencia
    asistencia = await db.get(Asistencia, data.asistencia_id)
    if not asistencia:
        raise HTTPException(status_code=404, detail="El registro de asistencia no existe.")
    
    # 2. Verificar que sea una falta (ausente)
    if asistencia.estado not in [EstadoAsistencia.AUSENTE, EstadoAsistencia.JUSTIFICADO]:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden justificar inasistencias (estado 'ausente'). "
                   f"El estado actual es '{asistencia.estado.value}'."
        )
    
    # 3. Verificar que la falta ya no esté justificada
    if asistencia.estado == EstadoAsistencia.JUSTIFICADO:
        raise HTTPException(
            status_code=409,
            detail="Esta falta ya ha sido justificada anteriormente."
        )
    
    # 4. Verificar que la falta pertenezca al alumno
    if asistencia.alumno_id != alumno_id:
        raise HTTPException(
            status_code=403,
            detail="No puede justificar una falta que no pertenece a su hijo."
        )
    
    # 5. Verificar si ya existe una justificación para esta falta
    existente = await obtener_justificacion_por_asistencia(db, data.asistencia_id)
    if existente:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe una justificación para esta falta. Estado actual: {existente.estado.value}."
        )
    
    # 6. Verificar límite de justificaciones virtuales
    verificacion = await verificar_justificaciones_virtuales_disponibles(db, alumno_id)
    if not verificacion["puede_justificar_virtualmente"]:
        raise HTTPException(
            status_code=403,
            detail=verificacion["mensaje"]
        )
    
    # 7. Crear la justificación
    nueva_justificacion = Justificacion(
        asistencia_id=data.asistencia_id,
        motivo=data.motivo,
        archivo_sustento_url=data.archivo_sustento_url,
        estado=EstadoTramiteJustificacion.PENDIENTE
    )
    
    db.add(nueva_justificacion)
    await db.commit()
    await db.refresh(nueva_justificacion)
    
    return nueva_justificacion

async def aprobar_justificacion(
    db: AsyncSession,
    justificacion_id: int,
    data: JustificacionUpdateAuxiliar,
    auxiliar_id: int
) -> Justificacion:
    """
    El Auxiliar aprueba o rechaza una justificación.
    
    Si se aprueba:
    - La justificación pasa a estado 'aprobada'
    - La asistencia pasa a estado 'justificado'
    
    Si se rechaza:
    - La justificación pasa a estado 'rechazada'
    - La asistencia se mantiene como 'ausente'
    - DEBE incluir observación del motivo del rechazo
    """
    
    justificacion = await obtener_justificacion_por_id(db, justificacion_id)
    if not justificacion:
        raise HTTPException(status_code=404, detail="Justificación no encontrada.")
    
    # Verificar que esté pendiente
    if not justificacion.esta_pendiente:
        raise HTTPException(
            status_code=400,
            detail=f"La justificación ya fue {justificacion.estado.value}. "
                   "Solo se pueden revisar justificaciones pendientes."
        )
    
    # Validar que sea auxiliar
    from app.modules.usuarios.models import Usuario
    auxiliar = await db.get(Usuario, auxiliar_id)
    if not auxiliar or auxiliar.rol not in ['auxiliar', 'admin']:
        raise HTTPException(
            status_code=403,
            detail="Solo el Auxiliar o Admin pueden revisar justificaciones."
        )
    
    # Si rechaza, la observación es obligatoria
    if data.estado == 'rechazada' and not data.observacion_auxiliar:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar una observación explicando por qué se rechaza la justificación."
        )
    
    if data.estado == 'aprobada':
        justificacion.aprobar(data.observacion_auxiliar)
    else:
        justificacion.rechazar(data.observacion_auxiliar)
    
    await db.commit()
    await db.refresh(justificacion)
    
    return justificacion

# ═══════════════════════════════════════════════════════════════
# ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════

async def obtener_estadisticas_justificaciones(db: AsyncSession) -> dict:
    """Obtiene estadísticas generales de justificaciones"""
    
    # Total por estado
    resultado = await db.execute(
        select(Justificacion.estado, func.count(Justificacion.id))
        .group_by(Justificacion.estado)
    )
    por_estado = {estado: cantidad for estado, cantidad in resultado.all()}
    
    total_pendientes = por_estado.get('pendiente', 0)
    total_aprobadas = por_estado.get('aprobada', 0)
    total_rechazadas = por_estado.get('rechazada', 0)
    total_general = total_pendientes + total_aprobadas + total_rechazadas
    
    porcentaje_aprobacion = round(
        (total_aprobadas / (total_aprobadas + total_rechazadas) * 100)
        if (total_aprobadas + total_rechazadas) > 0 else 0,
        1
    )
    
    return {
        "total_pendientes": total_pendientes,
        "total_aprobadas": total_aprobadas,
        "total_rechazadas": total_rechazadas,
        "total_general": total_general,
        "porcentaje_aprobacion": porcentaje_aprobacion,
        "fecha_consulta": date.today()
    }