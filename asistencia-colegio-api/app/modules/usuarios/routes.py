from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioResponse
from app.modules.usuarios import services

# 1. Creamos el enrutador con su prefijo y etiquetas para la documentación automática (Swagger)
router = APIRouter(
    prefix="/usuarios",
    tags=["Personal / Usuarios del Sistema"]
)

# 2. Ruta para registrar un nuevo usuario (Solo el Admin debería usar esto más adelante)
@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def registrar_usuario(
    usuario_in: UsuarioCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Registra un nuevo miembro del personal (Admin, Auxiliar o Docente).
    Valida automáticamente que el DNI y Correo sean únicos.
    """
    return await services.crear_nuevo_usuario(db=db, usuario_data=usuario_in)

# 3. Ruta para buscar un usuario específico por su ID
@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario_por_id(
    usuario_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Busca y devuelve la información de un usuario según su ID único.
    """
    usuario = await services.obtener_usuario_por_id(db=db, usuario_id=usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario solicitado no existe en el sistema escolar."
        )
    return usuario

# 4. Ruta para buscar un usuario rápido ingresando su número de DNI
@router.get("/dni/{dni}", response_model=UsuarioResponse)
async def obtener_usuario_por_dni(
    dni: str, 
    db: AsyncSession = Depends(get_db)
):
    """
    Busca a un miembro del personal utilizando directamente su número de DNI.
    """
    if len(dni) != 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formato del DNI es inválido. Debe contener exactamente 8 dígitos."
        )
        
    usuario = await services.obtener_usuario_por_dni(db=db, dni=dni)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ningún trabajador registrado con el DNI proporcionado."
        )
    return usuario