from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.security import decodificar_token, extraer_jti
from app.core.database import get_db
from app.modules.usuarios.models import Usuario, RolUsuario
from app.modules.apoderados.models import Apoderado

security_scheme = HTTPBearer(auto_error=False)

# ═══════════════════════════════════════════════════════════════
# DEPENDENCIA: OBTENER USUARIO ACTUAL (PERSONAL)
# ═══════════════════════════════════════════════════════════════

async def obtener_usuario_actual(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[Usuario]:
    """
    Dependencia para obtener el usuario del personal autenticado.
    Usar en endpoints que requieran autenticación del colegio.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido. Use el header Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    payload = decodificar_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Inicie sesión nuevamente."
        )
    
    if payload.get("tipo_usuario") != "personal":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este endpoint es solo para personal del colegio."
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token no contiene user_id.")
    
    usuario = await db.get(Usuario, int(user_id))
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado.")
    
    if usuario.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Su cuenta está inactiva o en licencia."
        )
    
    return usuario

# ═══════════════════════════════════════════════════════════════
# DEPENDENCIA: OBTENER APODERADO ACTUAL (PADRE)
# ═══════════════════════════════════════════════════════════════

async def obtener_apoderado_actual(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[Apoderado]:
    """
    Dependencia para obtener el apoderado autenticado.
    Usar en endpoints de la App Familiar.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido."
        )
    
    token = credentials.credentials
    payload = decodificar_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")
    
    if payload.get("tipo_usuario") != "apoderado":
        raise HTTPException(status_code=403, detail="Endpoint solo para apoderados.")
    
    apoderado_id = payload.get("apoderado_id")
    if not apoderado_id:
        raise HTTPException(status_code=401, detail="Token no contiene apoderado_id.")
    
    apoderado = await db.get(Apoderado, int(apoderado_id))
    if not apoderado:
        raise HTTPException(status_code=401, detail="Apoderado no encontrado.")
    
    return apoderado

# ═══════════════════════════════════════════════════════════════
# DEPENDENCIAS POR ROL (CONTROL DE ACCESO)
# ═══════════════════════════════════════════════════════════════

class VerificadorRol:
    """Factory de dependencias para verificar roles específicos"""
    
    def __init__(self, roles_permitidos: list):
        self.roles_permitidos = roles_permitidos
    
    async def __call__(self, usuario: Usuario = Depends(obtener_usuario_actual)):
        if usuario.rol not in self.roles_permitidos:
            roles_str = ", ".join(self.roles_permitidos)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {roles_str}. Su rol: {usuario.rol.value}"
            )
        return usuario

# Instancias predefinidas para usar en los routers
solo_admin = VerificadorRol([RolUsuario.admin])
solo_auxiliar = VerificadorRol([RolUsuario.auxiliar, RolUsuario.admin])
solo_docente = VerificadorRol([RolUsuario.docente, RolUsuario.admin])
solo_docente_o_auxiliar = VerificadorRol([RolUsuario.docente, RolUsuario.auxiliar, RolUsuario.admin])