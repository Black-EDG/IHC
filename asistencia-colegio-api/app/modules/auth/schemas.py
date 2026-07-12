from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str

class PadreLoginRequest(BaseModel):
    dni: str = Field(..., min_length=8, max_length=8, pattern=r'^\d{8}$')

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombres: str