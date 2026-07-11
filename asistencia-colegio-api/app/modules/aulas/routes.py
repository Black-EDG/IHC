from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.modules.aulas.schemas import AulaCreate, AulaResponse
from app.modules.aulas import services

router = APIRouter(
    prefix="/aulas",
    tags=["Infraestructura / Aulas Escolares"]
)

@router.post("/", response_model=AulaResponse, status_code=status.HTTP_201_CREATED)
async def registrar_aula(
    aula_in: AulaCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Crea una nueva sección escolar para un año académico."""
    return await services.crear_nueva_aula(db=db, aula_data=aula_in)

@router.get("/", response_model=List[AulaResponse])
async def listar_aulas(db: AsyncSession = Depends(get_db)):
    """Devuelve el catálogo completo de aulas ordenadas por grado y sección."""
    return await services.listar_todas_las_aulas(db=db)

@router.get("/{aula_id}", response_model=AulaResponse)
async def obtener_aula(aula_id: int, db: AsyncSession = Depends(get_db)):
    """Busca los detalles de un salón específico ingresando su ID."""
    aula = await services.obtener_aula_por_id(db=db, aula_id=aula_id)
    if not aula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El aula solicitada no existe en la infraestructura del plantel."
        )
    return aula