from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import UsuarioCreate
from app.core.security import obtener_contrasena_hash

async def obtener_usuario_por_id(db: AsyncSession, usuario_id: int):
    """Busca un usuario por su Llave Primaria (ID)"""
    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    return resultado.scalars().first()

async def obtener_usuario_por_dni(db: AsyncSession, dni: str):
    """Busca un usuario por su DNI"""
    resultado = await db.execute(select(Usuario).where(Usuario.dni == dni))
    return resultado.scalars().first()

async def obtener_usuario_por_correo(db: AsyncSession, correo: str):
    """Busca un usuario por su Correo Electrónico"""
    resultado = await db.execute(select(Usuario).where(Usuario.correo == correo))
    return resultado.scalars().first()

async def crear_nuevo_usuario(db: AsyncSession, usuario_data: UsuarioCreate):
    """Lógica completa para registrar un nuevo usuario en el sistema"""
    
    # 1. Validación de Seguridad: Verificar que el DNI no exista
    usuario_existente_dni = await obtener_usuario_por_dni(db, usuario_data.dni)
    if usuario_existente_dni:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El DNI ya se encuentra registrado en el sistema escolar."
        )
        
    # 2. Validación de Seguridad: Verificar que el Correo no exista
    usuario_existente_correo = await obtener_usuario_por_correo(db, usuario_data.correo)
    if usuario_existente_correo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está asignado a otro miembro del personal."
        )

    # 3. Encriptar la contraseña limpia antes de mandarla a la base de datos
    hash_password = obtener_contrasena_hash(usuario_data.contrasena)

    # 4. Mapear el esquema de Pydantic al modelo de SQLAlchemy (excluyendo la clave limpia)
    datos_usuario = usuario_data.model_dump(exclude={"contrasena"})
    nuevo_usuario = Usuario(**datos_usuario, contrasena_hash=hash_password)

    # 5. Insertar y guardar los cambios de forma asíncrona en PostgreSQL
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario) # Carga el ID autogenerado y el creado_en
    
    return nuevo_usuario