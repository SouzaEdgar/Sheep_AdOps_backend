from fastapi import APIRouter
from pydantic import BaseModel
from services.url_services import process_urls_async

router = APIRouter()

# ===== Modelo de Request ===== #
class VerificarRequest(BaseModel):
    urls: list[str]
    parametros: list[str] = []

# ===== Rota de Verificação (levar resultados) ===== #
@router.post("/verificar")
async def verificar_urls(data: VerificarRequest):
    # --- Processar URLs --- #
    resultados = await process_urls_async(data.urls, data.parametros)
    return {"resultados": resultados}
