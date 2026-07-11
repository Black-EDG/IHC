from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1. Creamos el motor asíncrono conectado a PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Cambia a True si quieres ver las consultas SQL nativas en tu consola
    pool_pre_ping=True,  # Verifica si la conexión sigue viva antes de usarla
)

# 2. Configura la fábrica de sesiones asíncronas
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Clase Base para que nuestros futuros Modelos hereden de aquí
Base = declarative_base()

# 4. Dependencia que usaremos en las rutas de FastAPI para inyectar la BD
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()