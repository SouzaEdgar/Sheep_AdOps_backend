from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.url_services import process_urls_async

router = APIRouter()

# ===== Modelo de Request ===== #
class VerificarRequest(BaseModel):
    urls: list[str]
    parametros: list[str] = []

MAX_URLS = 120
# ===== Rota de Verificação (SSE) ===== #
@router.post("/verificar")
async def verificar_urls(request: Request, data: VerificarRequest):
    urls = data.urls[:MAX_URLS]
    parametros = data.parametros

    # --- Processar URLs --- #
    async def event_stream():
        async for resultado in process_urls_async(urls, parametros):
            yield f"data: {resultado}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
