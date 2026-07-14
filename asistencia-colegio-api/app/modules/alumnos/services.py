from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import date, datetime

from app.modules.alumnos.models import Alumno, EstadoAlumno
from app.modules.alumnos.schemas import (
    AlumnoCreate, 
    AlumnoUpdate, 
    SuspensionRequest,
    TrasladoRequest,
    AlumnoResumenAsistenciaResponse
)
from app.modules.aulas.models import Aula
from app.modules.apoderados.models import Apoderado

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════

async def obtener_alumno_por_id(db: AsyncSession, alumno_id: int) -> Optional[Alumno]:
    """Busca alumno por ID con todas sus relaciones precargadas"""
    resultado = await db.execute(
        select(Alumno)
        .options(
            selectinload(Alumno.aula),
            selectinload(Alumno.apoderado),
            selectinload(Alumno.asistencias)
        )
        .where(Alumno.id == alumno_id)
    )
    return resultado.scalars().first()

async def obtener_alumno_por_dni(db: AsyncSession, dni: str) -> Optional[Alumno]:
    """Busca alumno por DNI con relaciones precargadas"""
    resultado = await db.execute(
        select(Alumno)
        .options(
            selectinload(Alumno.aula),
            selectinload(Alumno.apoderado)
        )
        .where(Alumno.dni == dni)
    )
    return resultado.scalars().first()

async def obtener_todos_los_alumnos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    aula_id: Optional[int] = None,
    apoderado_id: Optional[int] = None,
    buscar: Optional[str] = None,
    grado: Optional[int] = None
) -> List[Alumno]:
    """
    Lista todos los alumnos con múltiples filtros.
    Este es el endpoint principal del dashboard administrativo.
    """
    query = select(Alumno).options(
        selectinload(Alumno.aula),
        selectinload(Alumno.apoderado)
    )
    
    # Filtro por estado
    if estado:
        query = query.where(Alumno.estado == estado)
    
    # Filtro por aula específica
    if aula_id:
        query = query.where(Alumno.aula_id == aula_id)
    
    # Filtro por apoderado
    if apoderado_id:
        query = query.where(Alumno.apoderado_id == apoderado_id)
    
    # Filtro por grado (requiere JOIN con aulas)
    if grado:
        query = query.join(Aula).where(Aula.grado == grado)
    
    # Búsqueda por DNI o nombre
    if buscar:
        search_term = f"%{buscar}%"
        query = query.where(
            or_(
                Alumno.dni.ilike(search_term),
                Alumno.nombres.ilike(search_term),
                Alumno.apellidos.ilike(search_term)
            )
        )
    
    query = query.order_by(Alumno.apellidos).offset(skip).limit(limit)
    resultado = await db.execute(query)
    return resultado.scalars().all()

async def obtener_alumnos_por_aula(db: AsyncSession, aula_id: int) -> List[Alumno]:
    """
    Obtiene todos los alumnos de un aula específica.
    Usado por el docente/tutor para pasar asistencia.
    """
    resultado = await db.execute(
        select(Alumno)
        .options(selectinload(Alumno.apoderado))
        .where(
            and_(
                Alumno.aula_id == aula_id,
                Alumno.estado == EstadoAlumno.MATRICULADO
            )
        )
        .order_by(Alumno.apellidos)
    )
    return resultado.scalars().all()

async def obtener_alumnos_por_apoderado(db: AsyncSession, apoderado_id: int) -> List[Alumno]:
    """
    Obtiene todos los hijos de un apoderado.
    Usado en la bandeja de selección de la App Familiar.
    """
    resultado = await db.execute(
        select(Alumno)
        .options(selectinload(Alumno.aula))
        .where(Alumno.apoderado_id == apoderado_id)
        .order_by(Alumno.aula_id)
    )
    return resultado.scalars().all()

# ═══════════════════════════════════════════════════════════════
# OPERACIONES CRUD
# ═══════════════════════════════════════════════════════════════

async def crear_alumno(db: AsyncSession, alumno_data: AlumnoCreate) -> Alumno:
    """
    Matricula un nuevo alumno en el sistema con validaciones completas.
    """
    
    # Validar DNI único
    existente = await obtener_alumno_por_dni(db, alumno_data.dni)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El DNI {alumno_data.dni} ya está registrado para el alumno {existente.nombre_completo}."
        )
    
    # Validar que el aula exista y tenga cupo
    aula = await db.get(Aula, alumno_data.aula_id)
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El aula con ID {alumno_data.aula_id} no existe."
        )
    
    # Validar que el apoderado exista
    apoderado = await db.get(Apoderado, alumno_data.apoderado_id)
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El apoderado con ID {alumno_data.apoderado_id} no existe. "
                    "Debe registrar al apoderado primero."
        )
    
    # Crear instancia
    datos = alumno_data.model_dump()
    nuevo_alumno = Alumno(**datos)
    
    db.add(nuevo_alumno)
    await db.commit()
    await db.refresh(nuevo_alumno)
    
    return nuevo_alumno

async def actualizar_alumno(
    db: AsyncSession, 
    alumno_id: int, 
    alumno_data: AlumnoUpdate
) -> Optional[Alumno]:
    """
    Actualiza los datos de un alumno existente.
    """
    alumno = await obtener_alumno_por_id(db, alumno_id)
    
    if not alumno:
        return None
    
    update_data = alumno_data.model_dump(exclude_unset=True)
    
    # Si cambia de aula, validar que la nueva exista
    if 'aula_id' in update_data:
        nueva_aula = await db.get(Aula, update_data['aula_id'])
        if not nueva_aula:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El aula con ID {update_data['aula_id']} no existe."
            )
    
    # Si cambia de apoderado, validar que exista
    if 'apoderado_id' in update_data:
        nuevo_apoderado = await db.get(Apoderado, update_data['apoderado_id'])
        if not nuevo_apoderado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El apoderado con ID {update_data['apoderado_id']} no existe."
            )
    
    for key, value in update_data.items():
        if hasattr(alumno, key):
            setattr(alumno, key, value)
    
    await db.commit()
    await db.refresh(alumno)
    return alumno

async def eliminar_alumno(db: AsyncSession, alumno_id: int) -> bool:
    """
    Elimina un alumno solo si no tiene asistencias registradas.
    Si tiene asistencias, se recomienda marcarlo como 'retirado' en lugar de eliminarlo.
    """
    alumno = await obtener_alumno_por_id(db, alumno_id)
    
    if not alumno:
        return False
    
    # Verificar dependencias
    if alumno.asistencias:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar al alumno {alumno.nombre_completo} porque tiene "
                    f"{len(alumno.asistencias)} registros de asistencia. "
                    "Considere cambiar su estado a 'retirado' en lugar de eliminarlo."
        )
    
    await db.delete(alumno)
    await db.commit()
    return True

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE NEGOCIO
# ═══════════════════════════════════════════════════════════════

async def suspender_alumno(
    db: AsyncSession, 
    alumno_id: int, 
    suspension: SuspensionRequest
) -> Optional[Alumno]:
    """
    Suspende a un alumno por un período determinado.
    Registra las fechas de inicio y fin de la suspensión.
    """
    alumno = await obtener_alumno_por_id(db, alumno_id)
    
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alumno con ID {alumno_id} no encontrado."
        )
    
    if not alumno.esta_matriculado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede suspender a alumnos con estado 'matriculado'."
        )
    
    try:
        alumno.suspender(desde=suspension.desde, hasta=suspension.hasta)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    await db.commit()
    await db.refresh(alumno)
    return alumno

async def levantar_suspension(db: AsyncSession, alumno_id: int) -> Optional[Alumno]:
    """
    Elimina la suspensión activa de un alumno.
    """
    alumno = await obtener_alumno_por_id(db, alumno_id)
    
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alumno con ID {alumno_id} no encontrado."
        )
    
    if not alumno.esta_suspendido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El alumno no tiene una suspensión activa."
        )
    
    alumno.levantar_suspension()
    await db.commit()
    await db.refresh(alumno)
    return alumno

async def trasladar_alumno(
    db: AsyncSession, 
    alumno_id: int, 
    traslado: TrasladoRequest
) -> Optional[Alumno]:
    """
    Traslada a un alumno a otra aula (mismo grado, diferente sección).
    """
    alumno = await obtener_alumno_por_id(db, alumno_id)
    
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alumno con ID {alumno_id} no encontrado."
        )
    
    if not alumno.esta_matriculado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede trasladar a alumnos matriculados."
        )
    
    # Validar que el aula destino exista
    nueva_aula = await db.get(Aula, traslado.nueva_aula_id)
    if not nueva_aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El aula destino con ID {traslado.nueva_aula_id} no existe."
        )
    
    alumno.trasladar(traslado.nueva_aula_id)
    await db.commit()
    await db.refresh(alumno)
    return alumno

async def retirar_alumno(db: AsyncSession, alumno_id: int, motivo: str = None) -> Optional[Alumno]:
    """
    Retira oficialmente a un alumno del colegio.
    """
    alumno = await obtener_alumno_por_id(db, alumno_id)
    
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alumno con ID {alumno_id} no encontrado."
        )
    
    alumno.retirar()
    await db.commit()
    await db.refresh(alumno)
    return alumno

async def obtener_resumen_asistencias(
    db: AsyncSession, 
    alumno_id: int,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> AlumnoResumenAsistenciaResponse:
    """
    Obtiene el resumen de asistencias de un alumno en un período.
    Si no se especifican fechas, se usa el año escolar actual.
    """
    alumno = await obtener_alumno_por_id(db, alumno_id)
    
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alumno con ID {alumno_id} no encontrado."
        )
    
    # Si no se especifican fechas, usar año actual
    if not fecha_inicio:
        fecha_inicio = date(date.today().year, 1, 1)
    if not fecha_fin:
        fecha_fin = date.today()
    
    resumen = alumno.resumen_asistencias(fecha_inicio, fecha_fin)
    
    return AlumnoResumenAsistenciaResponse(
        alumno_id=alumno.id,
        alumno_nombre=alumno.nombre_completo,
        grado_seccion=alumno.grado_seccion,
        total_asistencias=resumen["total"],
        presentes=resumen["presentes"],
        ausentes=resumen["ausentes"],
        tardes=resumen["tardes"],
        justificados=resumen["justificados"],
        porcentaje_asistencia=resumen["porcentaje_asistencia"],
        riesgo_inhabilitacion=resumen["riesgo_inhabilitacion"]
    )

async def proceso_promocion_masiva(
    db: AsyncSession, 
    anio_actual: int
) -> dict:
    """
    Proceso automático de promoción de año escolar.
    
    Lógica:
    - Alumnos de 1° a 4°: Se mueven al siguiente grado, misma sección
    - Alumnos de 5°: Se gradúan (estado 'retirado')
    - Alumnos retirados/trasladados: No se procesan
    
    Este proceso se ejecuta UNA VEZ al finalizar el año escolar.
    """
    
    # Obtener aulas del año siguiente
    anio_siguiente = anio_actual + 1
    resultado_aulas = await db.execute(
        select(Aula).where(Aula.anio_escolar == anio_siguiente)
    )
    aulas_siguiente_anio = {f"{a.grado}-{a.seccion}": a for a in resultado_aulas.scalars().all()}
    
    # Obtener alumnos matriculados del año actual
    resultado_alumnos = await db.execute(
        select(Alumno)
        .options(selectinload(Alumno.aula))
        .where(
            and_(
                Alumno.estado == EstadoAlumno.MATRICULADO,
                Aula.anio_escolar == anio_actual
            )
        )
        .join(Aula)
    )
    alumnos = resultado_alumnos.scalars().all()
    
    total = len(alumnos)
    promovidos = 0
    graduados = 0
    no_promovidos = 0
    errores = []
    
    for alumno in alumnos:
        try:
            if alumno.aula.grado < 5:
                # Buscar aula equivalente en el siguiente año
                nueva_clave = f"{alumno.aula.grado + 1}-{alumno.aula.seccion}"
                nueva_aula = aulas_siguiente_anio.get(nueva_clave)
                
                if not nueva_aula:
                    errores.append(
                        f"No existe aula {alumno.aula.grado + 1}° {alumno.aula.seccion} "
                        f"para el año {anio_siguiente}. Alumno: {alumno.nombre_completo}"
                    )
                    no_promovidos += 1
                    continue
                
                alumno.aula_id = nueva_aula.id
                promovidos += 1
            else:
                # Es alumno de 5°, se gradúa
                alumno.estado = EstadoAlumno.RETIRADO
                graduados += 1
                
        except Exception as e:
            errores.append(f"Error con alumno {alumno.nombre_completo}: {str(e)}")
            no_promovidos += 1
    
    await db.commit()
    
    return {
        "total_procesados": total,
        "promovidos": promovidos,
        "graduados": graduados,
        "no_promovidos": no_promovidos,
        "errores": errores,
        "fecha_proceso": datetime.now(),
        "anio_origen": anio_actual,
        "anio_destino": anio_siguiente
    }

async def obtener_estadisticas_generales(db: AsyncSession) -> dict:
    """
    Obtiene estadísticas generales de todos los alumnos para el dashboard.
    """
    # Total de alumnos por estado
    resultado = await db.execute(
        select(Alumno.estado, func.count(Alumno.id))
        .group_by(Alumno.estado)
    )
    por_estado = {estado: cantidad for estado, cantidad in resultado.all()}
    
    # Total de alumnos suspendidos
    resultado_suspendidos = await db.execute(
        select(func.count(Alumno.id))
        .where(
            and_(
                Alumno.suspendido_desde <= date.today(),
                Alumno.suspendido_hasta >= date.today()
            )
        )
    )
    suspendidos = resultado_suspendidos.scalar()
    
    # Alumnos por grado
    resultado_por_grado = await db.execute(
        select(Aula.grado, func.count(Alumno.id))
        .join(Aula)
        .where(Alumno.estado == EstadoAlumno.MATRICULADO)
        .group_by(Aula.grado)
        .order_by(Aula.grado)
    )
    por_grado = {f"{grado}°": cantidad for grado, cantidad in resultado_por_grado.all()}
    
    return {
        "total_alumnos": sum(por_estado.values()),
        "por_estado": por_estado,
        "suspendidos_actualmente": suspendidos,
        "por_grado": por_grado,
        "fecha_consulta": date.today()
    }