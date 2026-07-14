from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# ═══════════════════════════════════════════════════════════════
# IMPORTACIÓN DE ROUTERS
# ═══════════════════════════════════════════════════════════════
from app.modules.auth import router as auth_router
from app.modules.usuarios import router as usuarios_router
from app.modules.apoderados import router as apoderados_router
from app.modules.alumnos import router as alumnos_router
from app.modules.aulas import router as aulas_router
from app.modules.cursos import router as cursos_router
from app.modules.asignaciones import router as asignaciones_router
from app.modules.asistencias import router as asistencias_router
from app.modules.justificaciones import router as justificaciones_router
from app.modules.alertas import router as alertas_router

# ═══════════════════════════════════════════════════════════════
# CREACIÓN DE LA APLICACIÓN
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="Sistema de Gestión y Monitoreo de Asistencia Escolar",
    description="""
    **API Backend profesional asíncrona para colegios nacionales del Perú.**
    
    ## 🏫 Módulos del Sistema
    
    | Módulo | Descripción |
    |--------|-------------|
    | 🔐 **Auth** | Autenticación JWT para personal y padres |
    | 👥 **Usuarios** | Gestión del personal (Admin, Auxiliar, Docente) |
    | 👨‍👩‍👧‍👦 **Apoderados** | Registro de padres de familia |
    | 🎒 **Alumnos** | Matrícula y control de estudiantes |
    | 🏫 **Aulas** | Gestión de grados y secciones |
    | 📚 **Cursos** | Materias del plan de estudios |
    | 🔗 **Asignaciones** | Vinculación Docentes-Aulas-Cursos |
    | ✅ **Asistencias** | Registro diario de asistencia |
    | 📝 **Justificaciones** | Justificación de inasistencias |
    | 🔔 **Alertas** | SMS automáticos y citaciones PDF |
    
    ## 🔐 Autenticación
    
    - **Personal**: Login con DNI + Contraseña → JWT Token
    - **Padres**: Login simplificado solo con DNI → JWT Token
    - **Seguridad opcional**: Verificación SMS para padres
    
    ## 📍 Alcance del Sistema
    
    Diseñado para colegios nacionales y particulares en zonas urbanas 
    y semiurbanas (ej. Abancay) con acceso a internet y telefonía móvil.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Soporte Técnico",
        "email": "soporte@colegioabancay.edu.pe",
    },
    license_info={
        "name": "Uso exclusivo del colegio",
    },
)

# ═══════════════════════════════════════════════════════════════
# MIDDLEWARE CORS
# ═══════════════════════════════════════════════════════════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization", 
        "Content-Type", 
        "Accept", 
        "Origin", 
        "X-Requested-With"
    ],
    expose_headers=["X-Total-Count", "X-Page"],
    max_age=600,  # Cache preflight por 10 minutos
)

# ═══════════════════════════════════════════════════════════════
# REGISTRO DE ROUTERS
# ═══════════════════════════════════════════════════════════════

# 1. Autenticación (sin prefijo, usa /auth)
app.include_router(auth_router)

# 2. Personal del colegio
app.include_router(usuarios_router)

# 3. Apoderados / Padres de familia
app.include_router(apoderados_router)

# 4. Alumnos / Estudiantes
app.include_router(alumnos_router)

# 5. Aulas / Salones
app.include_router(aulas_router)

# 6. Cursos / Materias
app.include_router(cursos_router)

# 7. Asignaciones (Docentes-Aulas-Cursos)
app.include_router(asignaciones_router)

# 8. Asistencias (Pase de lista)
app.include_router(asistencias_router)

# 9. Justificaciones de inasistencias
app.include_router(justificaciones_router)

# 10. Alertas (SMS y Citaciones PDF)
app.include_router(alertas_router)

# ═══════════════════════════════════════════════════════════════
# ENDPOINT RAÍZ
# ═══════════════════════════════════════════════════════════════

@app.get("/", tags=["🏠 Inicio"])
async def root():
    """
    **Endpoint raíz del sistema.**
    
    Retorna información básica del estado del servidor.
    """
    return {
        "status": "online",
        "mensaje": "Bienvenido al Sistema de Gestión y Monitoreo de Asistencia Escolar",
        "version": "1.0.0",
        "documentacion": "/docs",
        "documentacion_alternativa": "/redoc",
        "modulos_disponibles": [
            {"modulo": "Auth", "ruta": "/auth", "descripcion": "Autenticación JWT"},
            {"modulo": "Usuarios", "ruta": "/usuarios", "descripcion": "Personal del colegio"},
            {"modulo": "Apoderados", "ruta": "/apoderados", "descripcion": "Padres de familia"},
            {"modulo": "Alumnos", "ruta": "/alumnos", "descripcion": "Estudiantes"},
            {"modulo": "Aulas", "ruta": "/aulas", "descripcion": "Grados y secciones"},
            {"modulo": "Cursos", "ruta": "/cursos", "descripcion": "Materias"},
            {"modulo": "Asignaciones", "ruta": "/asignaciones", "descripcion": "Docentes-Aulas"},
            {"modulo": "Asistencias", "ruta": "/asistencias", "descripcion": "Pase de lista"},
            {"modulo": "Justificaciones", "ruta": "/justificaciones", "descripcion": "Justificar faltas"},
            {"modulo": "Alertas", "ruta": "/alertas", "descripcion": "SMS y citaciones"},
        ]
    }


@app.get("/health", tags=["🏠 Inicio"])
async def health_check():
    """
    **Endpoint de verificación de salud del servidor.**
    
    Útil para monitoreo y balanceadores de carga.
    """
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "timestamp": "2026-07-13T00:00:00Z"
    }


# ═══════════════════════════════════════════════════════════════
# EVENTOS DE INICIO/CIERRE
# ═══════════════════════════════════════════════════════════════

@app.on_event("startup")
async def evento_inicio():
    """
    Se ejecuta cuando el servidor inicia.
    Útil para tareas de inicialización.
    """
    print("🚀 Sistema de Asistencia Escolar iniciado correctamente.")
    print(f"📚 Documentación: http://localhost:8000/docs")
    print(f"📖 Documentación alternativa: http://localhost:8000/redoc")
    print(f"🏥 Health check: http://localhost:8000/health")
    print("=" * 60)


@app.on_event("shutdown")
async def evento_cierre():
    """
    Se ejecuta cuando el servidor se detiene.
    Útil para cerrar conexiones pendientes.
    """
    print("🛑 Sistema de Asistencia Escolar detenido.")


# ═══════════════════════════════════════════════════════════════
# MANEJADORES DE EXCEPCIONES GLOBALES
# ═══════════════════════════════════════════════════════════════

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Formatea los errores de validación de Pydantic en español.
    """
    errores = []
    for error in exc.errors():
        campo = " → ".join(str(loc) for loc in error["loc"])
        mensaje = error["msg"]
        errores.append(f"{campo}: {mensaje}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "tipo": "Error de Validación",
            "detalle": "Los datos enviados no son válidos.",
            "errores": errores
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Maneja errores de base de datos de forma genérica.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "tipo": "Error de Base de Datos",
            "detalle": "Ocurrió un error al procesar la solicitud en la base de datos."
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Captura cualquier excepción no manejada.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "tipo": "Error Interno",
            "detalle": "Ocurrió un error inesperado en el servidor."
        }
    )


# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN PARA EJECUCIÓN DIRECTA
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )