from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func, desc
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.modules.alertas.models import Alerta, TipoAlerta, EstadoAlerta
from app.modules.alumnos.models import Alumno, EstadoAlumno
from app.modules.apoderados.models import Apoderado
from app.modules.asistencias.models import Asistencia, EstadoAsistencia
from app.modules.justificaciones.models import Justificacion

# ═══════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════

UMBRAL_SMS = 3          # 3 faltas → SMS de advertencia
UMBRAL_CITACION = 5     # 5 faltas → Citación PDF
UMBRAL_BLOQUEO = 3      # 3 justificaciones virtuales consecutivas → Bloqueo

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════

async def obtener_alerta_por_id(db: AsyncSession, alerta_id: int) -> Optional[Alerta]:
    """Busca una alerta por ID con relaciones"""
    resultado = await db.execute(
        select(Alerta)
        .options(
            selectinload(Alerta.alumno),
            selectinload(Alerta.apoderado)
        )
        .where(Alerta.id == alerta_id)
    )
    return resultado.scalars().first()

async def obtener_todas_las_alertas(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    alumno_id: Optional[int] = None
) -> List[Alerta]:
    """Lista todas las alertas con filtros"""
    query = select(Alerta).options(
        selectinload(Alerta.alumno),
        selectinload(Alerta.apoderado)
    )
    
    if tipo:
        query = query.where(Alerta.tipo == tipo)
    if estado:
        query = query.where(Alerta.estado == estado)
    if alumno_id:
        query = query.where(Alerta.alumno_id == alumno_id)
    
    query = query.order_by(desc(Alerta.creado_en)).offset(skip).limit(limit)
    resultado = await db.execute(query)
    return resultado.scalars().all()

async def obtener_alertas_por_alumno(db: AsyncSession, alumno_id: int) -> List[Alerta]:
    """Obtiene todas las alertas de un alumno"""
    resultado = await db.execute(
        select(Alerta)
        .options(
            selectinload(Alerta.alumno),
            selectinload(Alerta.apoderado)
        )
        .where(Alerta.alumno_id == alumno_id)
        .order_by(desc(Alerta.creado_en))
    )
    return resultado.scalars().all()

async def obtener_alertas_por_apoderado(db: AsyncSession, apoderado_id: int) -> List[Alerta]:
    """Obtiene todas las alertas enviadas a un apoderado"""
    resultado = await db.execute(
        select(Alerta)
        .options(
            selectinload(Alerta.alumno),
            selectinload(Alerta.apoderado)
        )
        .where(Alerta.apoderado_id == apoderado_id)
        .order_by(desc(Alerta.creado_en))
    )
    return resultado.scalars().all()

# ═══════════════════════════════════════════════════════════════
# PROCESO AUTOMÁTICO DE DISPARO DE ALERTAS
# ═══════════════════════════════════════════════════════════════

async def contar_faltas_alumno(db: AsyncSession, alumno_id: int) -> int:
    """
    Cuenta las faltas (ausente + justificado) de un alumno en el año escolar actual.
    Solo cuenta asistencias generales (curso_id IS NULL).
    """
    anio_actual = date.today().year
    fecha_inicio = date(anio_actual, 1, 1)
    fecha_fin = date.today()
    
    resultado = await db.execute(
        select(func.count(Asistencia.id))
        .where(
            and_(
                Asistencia.alumno_id == alumno_id,
                Asistencia.curso_id.is_(None),  # Solo asistencia general
                Asistencia.fecha >= fecha_inicio,
                Asistencia.fecha <= fecha_fin,
                Asistencia.estado.in_([
                    EstadoAsistencia.AUSENTE,
                    EstadoAsistencia.JUSTIFICADO
                ])
            )
        )
    )
    return resultado.scalar() or 0

async def contar_justificaciones_consecutivas(db: AsyncSession, alumno_id: int) -> int:
    """
    Cuenta las justificaciones virtuales consecutivas de un alumno.
    """
    resultado = await db.execute(
        select(Justificacion)
        .join(Asistencia)
        .where(Asistencia.alumno_id == alumno_id)
        .order_by(desc(Justificacion.creado_en))
        .limit(10)
    )
    justificaciones = resultado.scalars().all()
    
    consecutivas = 0
    for j in justificaciones:
        if j.estado in ['pendiente', 'aprobada']:
            consecutivas += 1
        else:
            break
    
    return consecutivas

async def alerta_ya_enviada_hoy(
    db: AsyncSession, 
    alumno_id: int, 
    tipo: TipoAlerta
) -> bool:
    """Verifica si ya se envió una alerta del mismo tipo hoy para este alumno"""
    hoy = date.today()
    resultado = await db.execute(
        select(func.count(Alerta.id))
        .where(
            and_(
                Alerta.alumno_id == alumno_id,
                Alerta.tipo == tipo,
                func.date(Alerta.creado_en) == hoy
            )
        )
    )
    return (resultado.scalar() or 0) > 0

async def disparar_alertas_automaticas(db: AsyncSession) -> dict:
    """
    PROCESO AUTOMÁTICO PRINCIPAL.
    
    Se ejecuta diariamente (por un scheduler como Celery, APScheduler o cron).
    Recorre todos los alumnos matriculados y verifica:
    
    1. Si tiene 3 faltas → Genera Alerta SMS (si no se envió hoy)
    2. Si tiene 5 faltas → Genera Alerta Citación PDF (si no se envió hoy)
    3. Si tiene 3 justificaciones virtuales consecutivas → Alerta Bloqueo
    """
    
    # Obtener todos los alumnos matriculados
    resultado = await db.execute(
        select(Alumno)
        .options(
            selectinload(Alumno.apoderado),
            selectinload(Alumno.aula)
        )
        .where(Alumno.estado == EstadoAlumno.MATRICULADO)
    )
    alumnos = resultado.scalars().all()
    
    total_verificados = len(alumnos)
    alertas_sms = 0
    alertas_citacion = 0
    alertas_bloqueo = 0
    errores = []
    
    for alumno in alumnos:
        try:
            # Contar faltas del año escolar actual
            total_faltas = await contar_faltas_alumno(db, alumno.id)
            
            # Alerta 1: 3 faltas → SMS
            if total_faltas >= UMBRAL_SMS and total_faltas < UMBRAL_CITACION:
                if not await alerta_ya_enviada_hoy(db, alumno.id, TipoAlerta.SMS_3_FALTAS):
                    nueva_alerta = Alerta(
                        alumno_id=alumno.id,
                        apoderado_id=alumno.apoderado_id,
                        tipo=TipoAlerta.SMS_3_FALTAS,
                        estado=EstadoAlerta.ENVIADA,
                        detalle=f"Alumno acumula {total_faltas} faltas. SMS enviado al {alumno.apoderado.celular}."
                    )
                    db.add(nueva_alerta)
                    alertas_sms += 1
            
            # Alerta 2: 5 faltas → Citación PDF
            if total_faltas >= UMBRAL_CITACION:
                if not await alerta_ya_enviada_hoy(db, alumno.id, TipoAlerta.CITACION_5_FALTAS):
                    # Generar URL del PDF (en producción se generaría el PDF real)
                    pdf_url = f"/storage/citaciones/{alumno.id}_{date.today().isoformat()}.pdf"
                    
                    nueva_alerta = Alerta(
                        alumno_id=alumno.id,
                        apoderado_id=alumno.apoderado_id,
                        tipo=TipoAlerta.CITACION_5_FALTAS,
                        estado=EstadoAlerta.ENVIADA,
                        detalle=f"Alumno acumula {total_faltas} faltas. Citación generada.",
                        pdf_citacion_url=pdf_url
                    )
                    db.add(nueva_alerta)
                    alertas_citacion += 1
            
            # Alerta 3: Bloqueo de justificaciones virtuales
            justificaciones_consecutivas = await contar_justificaciones_consecutivas(db, alumno.id)
            if justificaciones_consecutivas >= UMBRAL_BLOQUEO:
                if not await alerta_ya_enviada_hoy(db, alumno.id, TipoAlerta.JUSTIFICACION_BLOQUEADA):
                    nueva_alerta = Alerta(
                        alumno_id=alumno.id,
                        apoderado_id=alumno.apoderado_id,
                        tipo=TipoAlerta.JUSTIFICACION_BLOQUEADA,
                        estado=EstadoAlerta.ENVIADA,
                        detalle=f"Alumno ha usado {justificaciones_consecutivas} justificaciones virtuales consecutivas. "
                                "La próxima debe ser presencial."
                    )
                    db.add(nueva_alerta)
                    alertas_bloqueo += 1
                    
        except Exception as e:
            errores.append(f"Error con alumno {alumno.nombre_completo}: {str(e)}")
    
    await db.commit()
    
    return {
        "fecha_proceso": date.today(),
        "total_alumnos_verificados": total_verificados,
        "alertas_sms_3_faltas": alertas_sms,
        "alertas_citacion_5_faltas": alertas_citacion,
        "alertas_bloqueo_justificacion": alertas_bloqueo,
        "total_alertas_generadas": alertas_sms + alertas_citacion + alertas_bloqueo,
        "errores": errores
    }

# ═══════════════════════════════════════════════════════════════
# OPERACIONES MANUALES
# ═══════════════════════════════════════════════════════════════

async def marcar_alerta_como_entregada(db: AsyncSession, alerta_id: int) -> Alerta:
    """
    Marca una alerta como entregada.
    - SMS: Cuando el proveedor confirma la entrega
    - Citación: Cuando se imprime y entrega físicamente
    """
    alerta = await obtener_alerta_por_id(db, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada.")
    
    alerta.marcar_como_entregada()
    await db.commit()
    await db.refresh(alerta)
    return alerta

async def obtener_estadisticas_alertas(db: AsyncSession) -> dict:
    """Estadísticas generales de alertas"""
    
    resultado = await db.execute(
        select(Alerta.tipo, func.count(Alerta.id))
        .group_by(Alerta.tipo)
    )
    por_tipo = {tipo: cantidad for tipo, cantidad in resultado.all()}
    
    resultado_estado = await db.execute(
        select(Alerta.estado, func.count(Alerta.id))
        .group_by(Alerta.estado)
    )
    por_estado = {estado: cantidad for estado, cantidad in resultado_estado.all()}
    
    return {
        "total_sms_enviados": por_tipo.get('sms_3_faltas', 0),
        "total_citaciones_generadas": por_tipo.get('citacion_5_faltas', 0),
        "total_bloqueos": por_tipo.get('justificacion_bloqueada', 0),
        "total_pendientes_entrega": por_estado.get('enviada', 0),
        "total_fallidas": por_estado.get('fallida', 0),
        "fecha_consulta": date.today()
    }