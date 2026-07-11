from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.apoderados.schemas import ApoderadoCreate, ApoderadoResponse
from app.modules.apoderados import services

router = APIRouter(
    prefix="/apoderados",
    tags=["Entorno Familiar / Apoderados"]
)

@router.post("/", response_model=ApoderadoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_apoderado(
    apoderado_in: ApoderadoCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Registra un nuevo padre de familia o apoderado titular."""
    return await services.crear_nuevo_apoderado(db=db, apoderado_data=apoderado_in)

@router.get("/dni/{dni}", response_model=ApoderadoResponse)
async def obtener_apoderado_dni(dni: str, db: AsyncSession = Depends(get_db)):
    """Busca un apoderado usando directamente su número de DNI."""
    apoderado = await services.obtener_apoderado_por_dni(db=db, dni=dni)
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ningún apoderado registrado con el DNI proporcionado."
        )
    return apoderado

@router.get("/{apoderado_id}", response_model=ApoderadoResponse)
async def obtener_apoderado_id(apoderado_id: int, db: AsyncSession = Depends(get_db)):
    """Busca la ficha de un apoderado ingresando su ID único."""
    apoderado = await services.obtener_apoderado_por_id(db=db, apoderado_id=apoderado_id)
    if not apoderado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El apoderado solicitado no figura en los registros familiares."
        )
    return apoderado