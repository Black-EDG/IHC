from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from app.core.security import (
    verificar_contrasena,
    crear_token_acceso,
    crear_token_refresh,
    decodificar_token,
    extraer_jti,
    generar_codigo_sms
)
from app.modules.auth.models import TokenRevocado
from app.modules.usuarios.models import Usuario, RolUsuario
from app.modules.apoderados.models import Apoderado

# ═══════════════════════════════════════════════════════════════
# LOGIN PERSONAL (ADMIN, AUXILIAR, DOCENTE) - CON CORREO
# ═══════════════════════════════════════════════════════════════

async def login_personal(
    db: AsyncSession,
    correo: str,        # ← CAMBIADO: Ahora recibe correo
    contrasena: str
) -> Dict[str, Any]:
    """
    Autentica a un miembro del personal escolar usando CORREO + CONTRASEÑA.
    
    Retorna:
    - access_token
    - refresh_token
    - Datos del usuario
    - Dashboard (si es docente/auxiliar)
    """
    
    # Buscar usuario por CORREO (no por DNI)
    resultado = await db.execute(
        select(Usuario)
        .options(selectinload(Usuario.asignaciones))
        .where(Usuario.correo == correo)  # ← CAMBIADO: Busca por correo
    )
    usuario = resultado.scalars().first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas. Verifique su correo institucional y contraseña."
        )
    
    # Verificar estado
    if usuario.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Su cuenta se encuentra inactiva o en licencia. Contacte al administrador."
        )
    
    # Verificar contraseña
    if not verificar_contrasena(contrasena, usuario.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas. Verifique su correo institucional y contraseña."
        )
    
    # Datos para el token
    token_data = {
        "user_id": usuario.id,
        "dni": usuario.dni,
        "rol": usuario.rol.value,
        "nombre": usuario.nombre_completo,
        "correo": usuario.correo
    }
    
    # Crear tokens
    access_token = crear_token_acceso(token_data, tipo_usuario="personal")
    refresh_token = crear_token_refresh(token_data, tipo_usuario="personal")
    
    # Construir dashboard según rol
    dashboard = None
    if usuario.rol in [RolUsuario.docente, RolUsuario.auxiliar]:
        from app.modules.asignaciones.services import obtener_dashboard_docente
        dashboard = await obtener_dashboard_docente(db, usuario.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "dni": usuario.dni,
            "nombre_completo": usuario.nombre_completo,
            "rol": usuario.rol.value,
            "correo": usuario.correo
        },
        "dashboard": dashboard
    }

# ═══════════════════════════════════════════════════════════════
# LOGIN APODERADO (PADRE DE FAMILIA) - CON DNI
# ═══════════════════════════════════════════════════════════════

async def login_apoderado_solo_dni(
    db: AsyncSession,
    dni: str
) -> Dict[str, Any]:
    """
    Login simplificado para padres: solo con DNI.
    Retorna token JWT + bandeja de hijos.
    
    Flujo pensado para baja alfabetización digital:
    - Sin contraseña
    - Sin correo electrónico
    - Solo necesita su DNI
    """
    
    # Buscar apoderado por DNI
    resultado = await db.execute(
        select(Apoderado)
        .options(selectinload(Apoderado.alumnos))
        .where(Apoderado.dni == dni)
    )
    apoderado = resultado.scalars().first()
    
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No se encontró un apoderado con DNI {dni}. Verifique que esté registrado."
        )
    
    # Verificar que tenga hijos activos
    hijos_activos = apoderado.obtener_hijos_activos()
    if not hijos_activos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{apoderado.nombre_completo} no tiene hijos matriculados actualmente."
        )
    
    # Formatear bandeja de hijos
    hijos_bandeja = [
        {
            "id": hijo.id,
            "nombre_completo": hijo.nombre_completo,
            "dni": hijo.dni,
            "grado_seccion": hijo.grado_seccion,
            "estado": hijo.estado.value if hijo.estado else "desconocido"
        }
        for hijo in hijos_activos
    ]
    
    # Datos para el token
    token_data = {
        "apoderado_id": apoderado.id,
        "dni": apoderado.dni,
        "nombre": apoderado.nombre_completo,
        "celular": apoderado.celular
    }
    
    # Crear tokens
    access_token = crear_token_acceso(token_data, tipo_usuario="apoderado")
    refresh_token = crear_token_refresh(token_data, tipo_usuario="apoderado")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "apoderado": {
            "id": apoderado.id,
            "dni": apoderado.dni,
            "nombre_completo": apoderado.nombre_completo,
            "celular": apoderado.celular,
            "parentesco": apoderado.parentesco
        },
        "hijos": hijos_bandeja,
        "mensaje": f"Bienvenido(a) {apoderado.nombre_completo}. Seleccione a su hijo para continuar."
    }

async def login_apoderado_con_sms(
    db: AsyncSession,
    dni: str,
    codigo_sms: str
) -> Dict[str, Any]:
    """
    Login para padres con verificación SMS (más seguro).
    """
    from app.core.security import verificar_codigo_sms
    
    # Primero verificar el código SMS
    if not verificar_codigo_sms(codigo_sms):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código SMS inválido o expirado. Solicite uno nuevo."
        )
    
    # Si el código es válido, proceder con login normal
    return await login_apoderado_solo_dni(db, dni)

# ═══════════════════════════════════════════════════════════════
# RENOVACIÓN DE TOKEN
# ═══════════════════════════════════════════════════════════════

async def renovar_access_token(
    db: AsyncSession,
    refresh_token_str: str
) -> Dict[str, Any]:
    """
    Renueva un access token usando un refresh token válido.
    """
    
    # Verificar que el refresh token sea válido
    payload = decodificar_token(refresh_token_str)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado. Inicie sesión nuevamente."
        )
    
    # Verificar que sea un refresh token
    if payload.get("tipo_token") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token proporcionado no es un refresh token."
        )
    
    # Verificar que no esté revocado
    jti = payload.get("jti")
    if jti:
        resultado = await db.execute(
            select(TokenRevocado).where(TokenRevocado.token_jti == jti)
        )
        if resultado.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Este refresh token ha sido revocado. Inicie sesión nuevamente."
            )
    
    # Extraer datos del payload original
    token_data = {
        k: v for k, v in payload.items() 
        if k not in ["exp", "iat", "jti", "tipo_token"]
    }
    tipo_usuario = payload.get("tipo_usuario", "personal")
    
    # Crear nuevo access token
    nuevo_access_token = crear_token_acceso(token_data, tipo_usuario=tipo_usuario)
    
    # Calcular expiración
    from app.core.config import settings
    expira_en = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # en segundos
    
    return {
        "access_token": nuevo_access_token,
        "token_type": "bearer",
        "expira_en": expira_en
    }

# ═══════════════════════════════════════════════════════════════
# LOGOUT (REVOCAR TOKEN)
# ═══════════════════════════════════════════════════════════════

async def cerrar_sesion(
    db: AsyncSession,
    token: str,
    tipo_usuario: str = "personal"
) -> bool:
    """
    Revoca un token agregándolo a la blacklist.
    """
    payload = decodificar_token(token)
    if not payload:
        # Si el token ya expiró, no hay nada que revocar
        return True
    
    jti = payload.get("jti")
    user_id = payload.get("user_id") or payload.get("apoderado_id")
    exp = payload.get("exp")
    
    if jti and exp:
        expira_en = datetime.fromtimestamp(exp, tz=timezone.utc)
        
        token_revocado = TokenRevocado(
            token_jti=jti,
            usuario_id=user_id,
            tipo_usuario=tipo_usuario,
            expira_en=expira_en
        )
        db.add(token_revocado)
        await db.commit()
    
    return True

# ═══════════════════════════════════════════════════════════════
# ENVIAR CÓDIGO SMS (PARA VERIFICACIÓN)
# ═══════════════════════════════════════════════════════════════

async def enviar_codigo_sms_login(
    db: AsyncSession,
    dni: str
) -> Dict[str, Any]:
    """
    Envía un código SMS al celular del apoderado para verificación.
    """
    resultado = await db.execute(
        select(Apoderado).where(Apoderado.dni == dni)
    )
    apoderado = resultado.scalars().first()
    
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado.")
    
    codigo = generar_codigo_sms()
    
    # En producción: enviar SMS real
    # await servicio_sms.enviar(apoderado.celular, f"Su código: {codigo}")
    
    return {
        "mensaje": f"Código de verificación enviado al celular {apoderado.celular}",
        "celular_enmascarado": f"{apoderado.celular[:3]}***{apoderado.celular[-3:]}",
        "codigo_desarrollo": codigo,  # SOLO EN DESARROLLO
        "expiracion_minutos": 5
    }