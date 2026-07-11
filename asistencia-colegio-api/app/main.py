from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.modules.usuarios import routes as usuarios_routes
from app.modules.aulas import routes as aulas_routes
from app.modules.apoderados import routes as apoderados_routes
from app.modules.alumnos import routes as alumnos_routes
from app.modules.asistencias import routes as asistencias_routes
from app.modules.auth import routes as auth_routes
# 1. Instanciamos FastAPI configurando los títulos para la documentación automática
app = FastAPI(
    title="Sistema de Gestión y Monitoreo de Asistencia Escolar",
    description="API Backend profesional asíncrona desarrollada con FastAPI y PostgreSQL.",
    version="1.0.0"
)

# 2. Configuración de los middlewares de Seguridad (CORS)
# Esto permite que tu aplicación de Flutter, React o Vue se conecte a la API sin ser bloqueada por el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se cambian los asteriscos por las URLs reales del frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# 3. Registramos los enrutadores de los módulos (El de usuarios es el primero)
app.include_router(auth_routes.router)
app.include_router(usuarios_routes.router)
app.include_router(aulas_routes.router)
app.include_router(apoderados_routes.router)
app.include_router(alumnos_routes.router)
app.include_router(asistencias_routes.router)

# 4. Ruta base de prueba (Sanity Check)
@app.get("/", tags=["Inicio"])
async def root():
    return {
        "status": "online",
        "mensaje": "Bienvenido al Sistema de Asistencia Escolar API",
        "version": "1.0.0"
    }