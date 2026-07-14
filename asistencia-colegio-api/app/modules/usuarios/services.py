from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.usuarios.models import Usuario, RolUsuario
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioUpdate
from app.core.security import obtener_contrasena_hash, verificar_contrasena

async def obtener_usuario_por_id(db: AsyncSession, usuario_id: int) -> Optional[Usuario]:
    """Busca un usuario por su ID"""
    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    return resultado.scalars().first()

async def obtener_usuario_por_dni(db: AsyncSession, dni: str) -> Optional[Usuario]:
    """Busca un usuario por DNI"""
    resultado = await db.execute(select(Usuario).where(Usuario.dni == dni))
    return resultado.scalars().first()

async def obtener_usuario_por_correo(db: AsyncSession, correo: str) -> Optional[Usuario]:
    """Busca un usuario por correo electrónico"""
    resultado = await db.execute(select(Usuario).where(Usuario.correo == correo))
    return resultado.scalars().first()

async def obtener_todos_los_usuarios(
    db: AsyncSession, 
    rol: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[Usuario]:
    """Devuelve usuarios con filtros y paginación"""
    query = select(Usuario)
    
    if rol:
        query = query.where(Usuario.rol == rol)
    
    if estado:
        query = query.where(Usuario.estado == estado)
    
    query = query.order_by(Usuario.apellidos).offset(skip).limit(limit)
    resultado = await db.execute(query)
    return resultado.scalars().all()

async def autenticar_usuario(db: AsyncSession, dni: str, contrasena: str) -> Optional[Usuario]:
    """Autentica a un usuario del personal por DNI y contraseña"""
    usuario = await obtener_usuario_por_dni(db, dni)
    
    if not usuario:
        return None
    
    if usuario.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Su cuenta se encuentra inactiva o en licencia. Contacte al administrador."
        )
    
    if not verificar_contrasena(contrasena, usuario.contrasena_hash):
        return None
    
    return usuario

async def crear_nuevo_usuario(db: AsyncSession, usuario_data: UsuarioCreate) -> Usuario:
    """Registra un nuevo usuario con validaciones exhaustivas"""
    
    # Validar DNI único
    usuario_existente_dni = await obtener_usuario_por_dni(db, usuario_data.dni)
    if usuario_existente_dni:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El DNI {usuario_data.dni} ya está registrado en el sistema."
        )
    
    # Validar correo único
    usuario_existente_correo = await obtener_usuario_por_correo(db, usuario_data.correo)
    if usuario_existente_correo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El correo {usuario_data.correo} ya está asignado a otro usuario."
        )

    # Encriptar contraseña
    hash_password = obtener_contrasena_hash(usuario_data.contrasena)
    
    # Crear instancia
    datos_usuario = usuario_data.model_dump(exclude={"contrasena"})
    nuevo_usuario = Usuario(**datos_usuario, contrasena_hash=hash_password)

    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    
    return nuevo_usuario

async def actualizar_usuario(db: AsyncSession, usuario_id: int, usuario_data: UsuarioUpdate) -> Optional[Usuario]:
    """Actualiza datos del usuario con validaciones"""
    
    db_usuario = await obtener_usuario_por_id(db, usuario_id)
    if not db_usuario:
        return None

    update_data = usuario_data.model_dump(exclude_unset=True)

    # Procesar cambio de contraseña
    if "contrasena" in update_data:
        nueva_pass = update_data.pop("contrasena")
        if nueva_pass and nueva_pass.strip():
            db_usuario.contrasena_hash = obtener_contrasena_hash(nueva_pass)

    # Validar cambio de correo
    if "correo" in update_data and update_data["correo"] != db_usuario.correo:
        correo_en_uso = await obtener_usuario_por_correo(db, update_data["correo"])
        if correo_en_uso:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nuevo correo electrónico ya está siendo usado por otro usuario."
            )

    # Aplicar actualizaciones
    for key, value in update_data.items():
        if hasattr(db_usuario, key):
            setattr(db_usuario, key, value)

    await db.commit()
    await db.refresh(db_usuario)
    return db_usuario

async def eliminar_usuario(db: AsyncSession, usuario_id: int) -> bool:
    """Elimina un usuario si no tiene dependencias activas"""
    
    db_usuario = await obtener_usuario_por_id(db, usuario_id)
    if not db_usuario:
        return False
    
    # Verificar dependencias
    if db_usuario.asignaciones:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: El usuario tiene asignaciones de aula activas. Reasígnalas primero."
        )
    
    if db_usuario.asistencias_registradas:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: El usuario tiene registros de asistencia. Considere marcarlo como 'inactivo' en su lugar."
        )
    
    await db.delete(db_usuario)
    await db.commit()
    return True