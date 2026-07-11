from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verificar_contrasena, crear_token_acceso
from app.modules.usuarios import services as usuarios_services
from app.modules.auth.schemas import LoginRequest, TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Seguridad / Autenticación"]
)

@router.post("/login", response_model=TokenResponse)
async def login(
    credenciales: LoginRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de inicio de sesión único.
    Verifica las credenciales del personal y retorna un token JWT válido.
    """
    # 1. Buscar al usuario por correo electrónico
    usuario = await usuarios_services.obtener_usuario_por_correo(db, credenciales.correo)
    
    # 2. Si el usuario no existe o está inactivo, lanzamos un error genérico (por seguridad)
    if not usuario or usuario.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El correo electrónico o la contraseña son incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Verificar si la contraseña coincide con el Hash guardado en pgAdmin
    contrasena_valida = verificar_contrasena(credenciales.contrasena, usuario.contrasena_hash)
    if not contrasena_valida:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El correo electrónico o la contraseña son incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 4. Preparar la información que viajará oculta dentro del Token (Payload)
    datos_token = {
        "sub": usuario.correo,
        "usuario_id": usuario.id,
        "rol": usuario.rol
    }
    
    # 5. Generar el Token JWT firmado
    jwt_token = crear_token_acceso(data=datos_token)
    
    # 6. Responderle al Frontend con éxito
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "rol": usuario.rol,
        "nombres": f"{usuario.nombres} {usuario.apellidos}"
    }