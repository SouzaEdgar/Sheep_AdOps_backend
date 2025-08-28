from fastapi import APIRouter, Form
from pydantic import BaseModel
from services.url_services import process_urls_async

import re

router = APIRouter()

class ResultRequest(BaseModel):
    url: str
    parameter: str = ""

# ===== Rota de Verificação (levar resultados) ===== #
@router.post("/verificar")
async def verificar_urls(
    url: str = Form(...), 
    parameter: str = Form("")
):
    # --- URLS --- #
    urls = []
    for linha in url.splitlines():
        if linha.strip():
            urls.append(linha.strip())
    
    # --- Parametros --- #
    params = []
    for p in re.split(r"[;\n,]+", parameter):
        if p.strip():
            params.append(p.strip())
    
    # --- Processar URLs --- #
    resultados = await process_urls_async(urls, params)

    # --- JSON --- #
    return {
        "resultados": resultados
    }
