from pydantic import BaseModel, EmailStr
from typing import Optional

# 1. Lo que envía el usuario desde la pantalla de Login
class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str

# 2. Lo que responde la API si el Login es correcto
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str  # Enviamos el rol para que el frontend sepa qué pantallas mostrar (Admin, Docente, Auxiliar)
    nombres: str