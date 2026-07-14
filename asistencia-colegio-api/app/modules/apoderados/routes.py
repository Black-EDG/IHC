from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.modules.apoderados import services
from app.modules.apoderados.schemas import (
    ApoderadoCreate,
    ApoderadoResponse,
    ApoderadoUpdate,
    ApoderadoLoginResponse,
    ApoderadoBusquedaResponse,
    VerificarCelularRequest,
    HijoBandejaResponse
)

router = APIRouter(
    prefix="/apoderados",
    tags=["👨‍👩‍👧‍👦 Apoderados / Padres de Familia"]
)

# ═══════════════════════════════════════════════════════════════
# ENDPOINT PRINCIPAL: LOGIN SIMPLIFICADO PARA PADRES
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/login/{dni}", 
    response_model=ApoderadoLoginResponse,
    summary="🎯 Login del Padre de Familia (App Familiar)"
)
async def login_apoderado(
    dni: str,
    db: AsyncSession = Depends(get_db)
):
    """
    **Endpoint principal de la App Familiar.**
    
    El padre ingresa SOLO su DNI y el sistema:
    1. Verifica que esté registrado como apoderado
    2. Busca todos sus hijos matriculados
    3. Retorna una bandeja para que seleccione a qué hijo quiere ver
    
    **Flujo diseñado para baja alfabetización digital:**
    - Sin contraseñas que recordar
    - Sin correos electrónicos
    - Solo necesita saber su número de DNI
    """
    if len(dni) != 8 or not dni.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DNI inválido. Debe contener exactamente 8 dígitos numéricos."
        )
    
    return await services.login_apoderado_por_dni(db=db, dni=dni)

# ═══════════════════════════════════════════════════════════════
# CRUD DE APODERADOS
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/", 
    response_model=ApoderadoResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo apoderado"
)
async def registrar_apoderado(
    apoderado_in: ApoderadoCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Registra un nuevo apoderado en el sistema escolar.
    
    **Datos requeridos:**
    - DNI del apoderado (será su identificador de login)
    - Nombres y apellidos completos
    - Celular (9 dígitos, para envío de SMS)
    - Parentesco con el alumno
    
    **Opcional:**
    - Contacto de emergencia (nombre, celular, parentesco)
    - Correo electrónico
    """
    return await services.crear_apoderado(db=db, apoderado_data=apoderado_in)

@router.get(
    "/", 
    response_model=List[ApoderadoResponse],
    summary="Listar todos los apoderados"
)
async def listar_apoderados(
    buscar: Optional[str] = Query(None, description="Buscar por DNI o nombre"),
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos los apoderados registrados con opción de búsqueda.
    
    **Filtros disponibles:**
    - buscar: Busca por DNI o nombre del apoderado
    """
    return await services.obtener_todos_los_apoderados(
        db=db, 
        skip=skip, 
        limit=limit, 
        buscar=buscar
    )

@router.get(
    "/buscar", 
    response_model=List[ApoderadoBusquedaResponse],
    summary="Búsqueda rápida de apoderados"
)
async def buscar_apoderados(
    query: str = Query(..., min_length=2, description="DNI o nombre a buscar"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint rápido para búsquedas desde el frontend administrativo.
    
    Busca por:
    - DNI exacto o parcial
    - Nombres
    - Apellidos
    """
    return await services.obtener_todos_los_apoderados(db=db, buscar=query, limit=10)

@router.get(
    "/celular/{celular}", 
    response_model=List[ApoderadoResponse],
    summary="Buscar apoderados por celular"
)
async def buscar_por_celular(
    celular: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca apoderados por su número de celular.
    
    Útil cuando:
    - Varios apoderados comparten el mismo número
    - Se necesita contactar por teléfono
    """
    if len(celular) != 9 or not celular.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de celular inválido. Debe contener 9 dígitos."
        )
    
    apoderados = await services.obtener_apoderados_por_celular(db=db, celular=celular)
    if not apoderados:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron apoderados con el celular {celular}."
        )
    return apoderados

@router.get(
    "/dni/{dni}", 
    response_model=ApoderadoResponse,
    summary="Buscar apoderado por DNI"
)
async def obtener_apoderado_por_dni(
    dni: str, 
    db: AsyncSession = Depends(get_db)
):
    """
    Busca la información completa de un apoderado por su DNI.
    """
    if len(dni) != 8 or not dni.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DNI inválido. Debe contener 8 dígitos."
        )
    
    apoderado = await services.obtener_apoderado_por_dni(db=db, dni=dni)
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró apoderado con DNI {dni}."
        )
    return apoderado

@router.get(
    "/{apoderado_id}", 
    response_model=ApoderadoResponse,
    summary="Buscar apoderado por ID"
)
async def obtener_apoderado_por_id(
    apoderado_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene los datos completos de un apoderado por su ID único.
    """
    apoderado = await services.obtener_apoderado_por_id(db=db, apoderado_id=apoderado_id)
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apoderado con ID {apoderado_id} no encontrado."
        )
    return apoderado

@router.get(
    "/{apoderado_id}/hijos", 
    response_model=List[HijoBandejaResponse],
    summary="Ver hijos de un apoderado"
)
async def ver_hijos_apoderado(
    apoderado_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna la lista de hijos activos de un apoderado.
    
    Este endpoint alimenta la bandeja de selección en la App Familiar.
    """
    apoderado = await services.obtener_apoderado_por_id(db=db, apoderado_id=apoderado_id)
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apoderado con ID {apoderado_id} no encontrado."
        )
    
    hijos = apoderado.to_bandeja_hijos()
    if not hijos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Este apoderado no tiene hijos matriculados actualmente."
        )
    
    return hijos

@router.get(
    "/{apoderado_id}/estadisticas",
    summary="Estadísticas del apoderado"
)
async def ver_estadisticas_apoderado(
    apoderado_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna estadísticas resumidas para el dashboard del apoderado:
    - Cantidad de hijos registrados
    - Hijos matriculados vs no matriculados
    - Estado de verificación del celular
    """
    return await services.obtener_estadisticas_apoderado(db=db, apoderado_id=apoderado_id)

@router.patch(
    "/{apoderado_id}", 
    response_model=ApoderadoResponse,
    summary="Actualizar datos del apoderado"
)
async def actualizar_apoderado(
    apoderado_id: int,
    apoderado_in: ApoderadoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza los datos de un apoderado existente.
    
    **Nota:** Si cambia el número de celular, la verificación SMS se reiniciará.
    """
    apoderado = await services.actualizar_apoderado(
        db=db, 
        apoderado_id=apoderado_id, 
        apoderado_data=apoderado_in
    )
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apoderado con ID {apoderado_id} no encontrado."
        )
    return apoderado

@router.delete(
    "/{apoderado_id}",
    summary="Eliminar apoderado"
)
async def eliminar_apoderado(
    apoderado_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina permanentemente a un apoderado del sistema.
    
    ⚠️ **Restricción:** No se puede eliminar si tiene hijos vinculados activos.
    Primero debe reasignar o retirar a los alumnos.
    """
    resultado = await services.eliminar_apoderado(db=db, apoderado_id=apoderado_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apoderado con ID {apoderado_id} no encontrado."
        )
    return {
        "mensaje": "Apoderado eliminado correctamente del sistema.",
        "status": "success"
    }

# ═══════════════════════════════════════════════════════════════
# VERIFICACIÓN DE CELULAR (PARA FUTURO ENVÍO DE SMS)
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/verificar-celular/enviar-codigo",
    summary="Enviar código SMS de verificación"
)
async def enviar_codigo_verificacion(
    dni: str = Query(..., description="DNI del apoderado", min_length=8, max_length=8),
    db: AsyncSession = Depends(get_db)
):
    """
    Envía un código de 4 dígitos por SMS al celular del apoderado.
    
    **Flujo de seguridad opcional:**
    1. El padre ingresa su DNI
    2. Recibe un código SMS en su celular
    3. Ingresa el código para confirmar su identidad
    
    Esto evita que cualquier persona con el DNI de otro padre pueda ver sus hijos.
    """
    return await services.enviar_codigo_verificacion_celular(db=db, dni=dni)

@router.post(
    "/verificar-celular/confirmar",
    summary="Confirmar código de verificación SMS"
)
async def confirmar_codigo_verificacion(
    verificacion: VerificarCelularRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica el código SMS recibido y marca el celular como verificado.
    
    Después de esto, el apoderado podrá:
    - Recibir alertas por SMS de inasistencias
    - Recibir notificaciones de citaciones
    - Justificar inasistencias desde la app
    """
    return await services.verificar_celular_apoderado(
        db=db, 
        dni=verificacion.dni, 
        codigo_ingresado=verificacion.codigo_sms
    )