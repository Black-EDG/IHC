from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import obtener_usuario_actual, obtener_apoderado_actual
from app.modules.auth import services
from app.modules.auth.schemas import (
    LoginPersonalRequest,
    LoginPersonalResponse,
    LoginApoderadoRequest,
    LoginApoderadoConSMSRequest,
    LoginApoderadoResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutResponse,
    VerificarTokenResponse
)
from app.modules.usuarios.models import Usuario
from app.modules.apoderados.models import Apoderado

router = APIRouter(
    prefix="/auth",
    tags=["🔐 Autenticación"]
)

# ═══════════════════════════════════════════════════════════════
# LOGIN PERSONAL (ADMIN, AUXILIAR, DOCENTE)
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/login/personal",
    response_model=LoginPersonalResponse,
    summary="Login del Personal Escolar"
)
async def login_personal(
    data: LoginPersonalRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    **Login para Admin, Auxiliar y Docentes.**
    
    Usa CORREO institucional + Contraseña.
    Retorna JWT + Dashboard según el rol.
    """
    # ✅ CORREGIDO: data.correo en vez de data.dni
    return await services.login_personal(db, data.correo, data.contrasena)


# ═══════════════════════════════════════════════════════════════
# LOGIN APODERADO (PADRE DE FAMILIA)
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/login/apoderado",
    response_model=LoginApoderadoResponse,
    summary="Login del Padre de Familia (Solo DNI)"
)
async def login_apoderado(
    data: LoginApoderadoRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login simplificado para padres: solo DNI."""
    return await services.login_apoderado_solo_dni(db, data.dni)


@router.post(
    "/login/apoderado/sms",
    response_model=LoginApoderadoResponse,
    summary="Login del Padre con verificación SMS"
)
async def login_apoderado_sms(
    data: LoginApoderadoConSMSRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login para padres con verificación SMS."""
    return await services.login_apoderado_con_sms(db, data.dni, data.codigo_sms)


@router.post(
    "/login/apoderado/enviar-sms",
    summary="Enviar código SMS para login"
)
async def enviar_sms_login(
    dni: str = Body(..., embed=True, description="DNI del apoderado"),
    db: AsyncSession = Depends(get_db)
):
    """Envía un código SMS al celular del apoderado."""
    return await services.enviar_codigo_sms_login(db, dni)


# ═══════════════════════════════════════════════════════════════
# RENOVACIÓN DE TOKEN
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Renovar Access Token"
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Renueva el access token usando el refresh token."""
    return await services.renovar_access_token(db, data.refresh_token)


# ═══════════════════════════════════════════════════════════════
# LOGOUT
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Cerrar sesión"
)
async def logout(
    token: str = Body(..., embed=True, description="Token a revocar"),
    tipo_usuario: str = Body("personal", embed=True, description="personal o apoderado"),
    db: AsyncSession = Depends(get_db)
):
    """Cierra la sesión revocando el token."""
    await services.cerrar_sesion(db, token, tipo_usuario)
    return {"mensaje": "Sesión cerrada correctamente. Token revocado.", "status": "success"}


# ═══════════════════════════════════════════════════════════════
# VERIFICACIÓN DE TOKEN
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/verificar",
    response_model=VerificarTokenResponse,
    summary="Verificar si un token es válido"
)
async def verificar_token(
    db: AsyncSession = Depends(get_db)
):
    """Verifica si el token actual es válido."""
    return {"valido": True, "mensaje": "Token válido"}


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS PROTEGIDOS
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/me/personal",
    summary="Datos del personal autenticado"
)
async def obtener_mi_perfil_personal(
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    """Retorna los datos del personal actualmente autenticado."""
    return {
        "id": usuario.id,
        "dni": usuario.dni,
        "nombre_completo": usuario.nombre_completo,
        "correo": usuario.correo,
        "rol": usuario.rol.value,
        "estado": usuario.estado.value
    }


@router.get(
    "/me/apoderado",
    summary="Datos del apoderado autenticado"
)
async def obtener_mi_perfil_apoderado(
    apoderado: Apoderado = Depends(obtener_apoderado_actual)
):
    """Retorna los datos del apoderado actualmente autenticado."""
    return {
        "id": apoderado.id,
        "dni": apoderado.dni,
        "nombre_completo": apoderado.nombre_completo,
        "celular": apoderado.celular,
        "parentesco": apoderado.parentesco,
        "hijos": apoderado.to_bandeja_hijos()
    }