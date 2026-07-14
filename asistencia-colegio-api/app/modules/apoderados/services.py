from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.apoderados.models import Apoderado
from app.modules.apoderados.schemas import (
    ApoderadoCreate, 
    ApoderadoUpdate,
    ApoderadoLoginResponse,
    HijoBandejaResponse
)
from app.core.security import generar_codigo_sms, verificar_codigo_sms

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════

async def obtener_apoderado_por_id(db: AsyncSession, apoderado_id: int) -> Optional[Apoderado]:
    """Busca apoderado por ID con sus hijos precargados"""
    resultado = await db.execute(
        select(Apoderado)
        .options(selectinload(Apoderado.alumnos))
        .where(Apoderado.id == apoderado_id)
    )
    return resultado.scalars().first()

async def obtener_apoderado_por_dni(db: AsyncSession, dni: str) -> Optional[Apoderado]:
    """Busca apoderado por DNI con sus hijos precargados"""
    resultado = await db.execute(
        select(Apoderado)
        .options(selectinload(Apoderado.alumnos))
        .where(Apoderado.dni == dni)
    )
    return resultado.scalars().first()

async def obtener_todos_los_apoderados(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    buscar: Optional[str] = None
) -> List[Apoderado]:
    """
    Lista todos los apoderados con búsqueda por nombre o DNI
    """
    query = select(Apoderado).options(selectinload(Apoderado.alumnos))
    
    if buscar:
        # Buscar por DNI o por nombre completo
        from sqlalchemy import or_
        search_term = f"%{buscar}%"
        query = query.where(
            or_(
                Apoderado.dni.ilike(search_term),
                Apoderado.nombres.ilike(search_term),
                Apoderado.apellidos.ilike(search_term)
            )
        )
    
    query = query.order_by(Apoderado.apellidos).offset(skip).limit(limit)
    resultado = await db.execute(query)
    return resultado.scalars().all()

async def obtener_apoderados_por_celular(db: AsyncSession, celular: str) -> List[Apoderado]:
    """
    Busca apoderados por número de celular (pueden ser varios si comparten teléfono)
    """
    resultado = await db.execute(
        select(Apoderado)
        .options(selectinload(Apoderado.alumnos))
        .where(Apoderado.celular == celular)
    )
    return resultado.scalars().all()

# ═══════════════════════════════════════════════════════════════
# OPERACIONES DE NEGOCIO
# ═══════════════════════════════════════════════════════════════

async def login_apoderado_por_dni(db: AsyncSession, dni: str) -> ApoderadoLoginResponse:
    """
    Flujo de login simplificado para padres:
    1. Ingresa solo su DNI
    2. El sistema busca al apoderado
    3. Retorna la bandeja con sus hijos para que seleccione
    
    Este es el endpoint principal de la App Familiar
    """
    apoderado = await obtener_apoderado_por_dni(db, dni)
    
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un apoderado con DNI {dni}. "
                    "Verifique que esté registrado en el sistema escolar."
        )
    
    # Obtener hijos activos formateados para la bandeja
    hijos_bandeja = apoderado.to_bandeja_hijos()
    
    if not hijos_bandeja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El apoderado {apoderado.nombre_completo} no tiene hijos activos "
                    "matriculados actualmente en el colegio."
        )
    
    # Construir respuesta para la app del padre
    return ApoderadoLoginResponse(
        id=apoderado.id,
        dni=apoderado.dni,
        nombre_completo=apoderado.nombre_completo,
        celular=apoderado.celular,
        hijos=hijos_bandeja,
        mensaje=f"Bienvenido(a) {apoderado.nombre_completo}. Seleccione a su hijo para continuar."
    )

async def crear_apoderado(db: AsyncSession, apoderado_data: ApoderadoCreate) -> Apoderado:
    """
    Registra un nuevo apoderado en el sistema con validaciones completas
    """
    
    # Validar DNI único
    existente_dni = await obtener_apoderado_por_dni(db, apoderado_data.dni)
    if existente_dni:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El DNI {apoderado_data.dni} ya está registrado como apoderado. "
                    "Un mismo DNI no puede tener dos registros de apoderado."
        )
    
    # Validar que el celular no esté duplicado para el mismo DNI
    # (Un mismo celular puede ser compartido por varios apoderados, ej: esposo y esposa)
    
    # Crear instancia
    datos = apoderado_data.model_dump()
    nuevo_apoderado = Apoderado(**datos)
    
    db.add(nuevo_apoderado)
    await db.commit()
    await db.refresh(nuevo_apoderado)
    
    return nuevo_apoderado

async def actualizar_apoderado(
    db: AsyncSession, 
    apoderado_id: int, 
    apoderado_data: ApoderadoUpdate
) -> Optional[Apoderado]:
    """
    Actualiza los datos de un apoderado existente
    """
    apoderado = await obtener_apoderado_por_id(db, apoderado_id)
    
    if not apoderado:
        return None
    
    update_data = apoderado_data.model_dump(exclude_unset=True)
    
    # Si se cambia el celular, resetear verificación
    if 'celular' in update_data and update_data['celular'] != apoderado.celular:
        apoderado.celular_verificado = 'N'
    
    # Aplicar cambios
    for key, value in update_data.items():
        if hasattr(apoderado, key):
            setattr(apoderado, key, value)
    
    await db.commit()
    await db.refresh(apoderado)
    return apoderado

async def eliminar_apoderado(db: AsyncSession, apoderado_id: int) -> bool:
    """
    Elimina un apoderado solo si no tiene hijos vinculados
    """
    apoderado = await obtener_apoderado_por_id(db, apoderado_id)
    
    if not apoderado:
        return False
    
    # Verificar que no tenga hijos activos
    if apoderado.alumnos:
        nombres_hijos = [alumno.nombre_completo for alumno in apoderado.alumnos]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar al apoderado porque tiene {len(apoderado.alumnos)} "
                    f"hijo(s) vinculado(s): {', '.join(nombres_hijos)}. "
                    "Primero reasigne o retire a los alumnos."
        )
    
    await db.delete(apoderado)
    await db.commit()
    return True

async def enviar_codigo_verificacion_celular(
    db: AsyncSession, 
    dni: str
) -> dict:
    """
    Envía un código SMS de 4 dígitos para verificar el celular del apoderado
    """
    apoderado = await obtener_apoderado_por_dni(db, dni)
    
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apoderado con DNI {dni} no encontrado."
        )
    
    # Generar código SMS (en producción se integra con proveedor SMS)
    codigo = generar_codigo_sms()
    
    # TODO: Integrar con servicio SMS real (Twilio, Infobip, etc.)
    # await servicio_sms.enviar(apoderado.celular, f"Su código de verificación: {codigo}")
    
    # En desarrollo, retornamos el código para pruebas
    return {
        "mensaje": f"Código de verificación enviado al celular {apoderado.celular}",
        "codigo_desarrollo": codigo,  # Solo en desarrollo
        "expiracion_minutos": 5
    }

async def verificar_celular_apoderado(
    db: AsyncSession, 
    dni: str, 
    codigo_ingresado: str
) -> Apoderado:
    """
    Verifica el código SMS y marca el celular como verificado
    """
    apoderado = await obtener_apoderado_por_dni(db, dni)
    
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apoderado con DNI {dni} no encontrado."
        )
    
    # Verificar código
    if not verificar_codigo_sms(codigo_ingresado):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de verificación inválido o expirado. Solicite uno nuevo."
        )
    
    # Marcar como verificado
    apoderado.celular_verificado = 'S'
    await db.commit()
    await db.refresh(apoderado)
    
    return apoderado

async def obtener_estadisticas_apoderado(db: AsyncSession, apoderado_id: int) -> dict:
    """
    Obtiene estadísticas resumidas para el dashboard del apoderado
    """
    apoderado = await obtener_apoderado_por_id(db, apoderado_id)
    
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apoderado ID {apoderado_id} no encontrado."
        )
    
    total_hijos = len(apoderado.alumnos)
    hijos_activos = len(apoderado.obtener_hijos_activos())
    
    return {
        "apoderado": apoderado.nombre_completo,
        "dni": apoderado.dni,
        "total_hijos_registrados": total_hijos,
        "hijos_matriculados": hijos_activos,
        "hijos_no_matriculados": total_hijos - hijos_activos,
        "celular_verificado": apoderado.celular_esta_verificado,
        "tiene_contacto_emergencia": apoderado.tiene_contacto_emergencia
    }