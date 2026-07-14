from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.modules.usuarios.schemas import (
    UsuarioCreate, 
    UsuarioResponse, 
    UsuarioUpdate, 
    UsuarioLoginResponse
)
from app.modules.usuarios import services

router = APIRouter(
    prefix="/usuarios",
    tags=["👥 Personal / Usuarios del Sistema"]
)

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def registrar_usuario(usuario_in: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    """
    Registra un nuevo miembro del personal escolar.
    
    - **Admin**: Control total del sistema
    - **Auxiliar**: Monitoreo de asistencia diaria general  
    - **Docente**: Pase de asistencia en sus cursos
    """
    return await services.crear_nuevo_usuario(db=db, usuario_data=usuario_in)

@router.post("/login", response_model=UsuarioLoginResponse)
async def login_usuario(
    dni: str = Query(..., description="DNI del personal", min_length=8, max_length=8),
    contrasena: str = Query(..., description="Contraseña de acceso"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de autenticación para el personal escolar (Admin, Auxiliar, Docente).
    Retorna los datos básicos del usuario autenticado.
    """
    usuario = await services.autenticar_usuario(db, dni, contrasena)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas. Verifique su DNI y contraseña."
        )
    return usuario

@router.get("/", response_model=List[UsuarioResponse])
async def obtener_todos_los_usuarios(
    rol: Optional[str] = Query(None, description="Filtrar por rol: admin, auxiliar, docente"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: activo, licencia, inactivo"),
    skip: int = Query(0, ge=0, description="Saltar registros (paginación)"),
    limit: int = Query(100, ge=1, le=500, description="Límite de registros"),
    db: AsyncSession = Depends(get_db)
):
    """Devuelve la lista completa del personal con filtros y paginación."""
    return await services.obtener_todos_los_usuarios(
        db=db, 
        rol=rol, 
        estado=estado, 
        skip=skip, 
        limit=limit
    )

@router.get("/dni/{dni}", response_model=UsuarioResponse)
async def obtener_usuario_por_dni(dni: str, db: AsyncSession = Depends(get_db)):
    """Busca a un miembro del personal por su DNI exacto."""
    if len(dni) != 8 or not dni.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Formato de DNI inválido. Debe contener exactamente 8 dígitos numéricos."
        )
    
    usuario = await services.obtener_usuario_por_dni(db=db, dni=dni)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontró ningún usuario con DNI {dni}."
        )
    return usuario

@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario_por_id(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """Busca y devuelve la información completa de un usuario por su ID."""
    usuario = await services.obtener_usuario_por_id(db=db, usuario_id=usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Usuario con ID {usuario_id} no encontrado."
        )
    return usuario

@router.patch("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int, 
    usuario_in: UsuarioUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza los datos de un usuario existente.
    - Se puede cambiar cualquier campo individualmente
    - La contraseña es opcional (solo se actualiza si se proporciona)
    """
    usuario = await services.actualizar_usuario(
        db=db, 
        usuario_id=usuario_id, 
        usuario_data=usuario_in
    )
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se puede actualizar: Usuario ID {usuario_id} no encontrado."
        )
    return usuario

@router.patch("/{usuario_id}/estado", response_model=UsuarioResponse)
async def cambiar_estado_usuario(
    usuario_id: int,
    nuevo_estado: str = Query(..., description="Nuevo estado: activo, licencia, inactivo"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint rápido para cambiar solo el estado de un usuario.
    Útil para suspensiones temporales o activaciones rápidas.
    """
    from app.modules.usuarios.models import EstadoUsuario
    
    if nuevo_estado not in [e.value for e in EstadoUsuario]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Valores permitidos: {[e.value for e in EstadoUsuario]}"
        )
    
    usuario = await services.obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario ID {usuario_id} no encontrado."
        )
    
    usuario.estado = nuevo_estado
    await db.commit()
    await db.refresh(usuario)
    return usuario

@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina permanentemente a un usuario del sistema.
    ⚠️ Solo se puede eliminar si no tiene asignaciones ni asistencias registradas.
    """
    resultado = await services.eliminar_usuario(db=db, usuario_id=usuario_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se puede eliminar: Usuario ID {usuario_id} no encontrado."
        )
    return {
        "mensaje": f"Usuario ID {usuario_id} eliminado correctamente del sistema.",
        "status": "success"
    }