from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import verificar_contrasena, crear_token_acceso
from app.modules.usuarios import services as usuarios_services
from app.modules.apoderados.services import obtener_apoderado_por_dni
from app.modules.alumnos.services import listar_hijos_por_apoderado
from app.modules.auth.schemas import LoginRequest, TokenResponse, PadreLoginRequest
from app.modules.alumnos.schemas import AlumnoResponse

router = APIRouter(prefix="/auth", tags=["Seguridad / Autenticación"])

# ------------------------------------------------------------------
# 1. LOGIN DEL PERSONAL (Admin, Docente, Auxiliar)
# ------------------------------------------------------------------
@router.post("/login", response_model=TokenResponse)
async def login_personal(
    credenciales: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Inicio de sesión para personal del colegio.
    Verifica correo y contraseña, retorna token JWT.
    """
    # Buscar usuario por correo
    usuario = await usuarios_services.obtener_usuario_por_correo(db, credenciales.correo)

    # Validar existencia y estado activo
    if not usuario or usuario.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El correo electrónico o la contraseña son incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar contraseña
    if not verificar_contrasena(credenciales.contrasena, usuario.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El correo electrónico o la contraseña son incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar token JWT con datos básicos
    datos_token = {
        "sub": usuario.correo,
        "usuario_id": usuario.id,
        "rol": usuario.rol.value  # .value para obtener string del Enum
    }
    jwt_token = crear_token_acceso(data=datos_token)

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "rol": usuario.rol.value,
        "nombres": f"{usuario.nombres} {usuario.apellidos}"
    }


# ------------------------------------------------------------------
# 2. LOGIN PARA PADRES DE FAMILIA (Solo DNI)
# ------------------------------------------------------------------
@router.post("/login/padres", response_model=List[AlumnoResponse])
async def login_padre(
    credenciales: PadreLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Inicio de sesión para padres/apoderados.
    Solo requiere el DNI del apoderado.
    Devuelve la lista de hijos para que seleccione cuál consultar.
    """
    # Buscar apoderado por DNI
    apoderado = await obtener_apoderado_por_dni(db, credenciales.dni)
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El DNI ingresado no está registrado como apoderado."
        )

    # Obtener hijos vinculados
    hijos = await listar_hijos_por_apoderado(db, apoderado.id)
    if not hijos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron estudiantes vinculados a este apoderado."
        )

    return hijos