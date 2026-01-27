from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from services.url_services import process_urls_stream
import json
import asyncio
from typing import List

router = APIRouter()

class VerificarRequest(BaseModel):
    urls: List[str]
    parametros: List[str] = []

MAX_URLS = 120

# ===== Rota Verificar ===== #
@router.post("/verificar")
async def verificar_urls(request: Request, data: VerificarRequest):
    urls = (data.urls or [])[:MAX_URLS]
    parametros = data.parametros or []

    if not urls:
        # --- Devolve rápido se vazio --- #
        return PlainTextResponse("", status_code=204, headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*")
        })

    async def gen():
        # --- Cabeçalhos de “anti-buffering” em alguns proxies --- #
        yield ": " + (" " * 1024) + "\n" # ---> Enviar 1024 bytes de dados para 'enganar' o buffer do Chrome

        pos = 0
        last_ping = asyncio.get_event_loop().time()

        async for resultado in process_urls_stream(urls, parametros):
            pos += 1
            line = json.dumps({
                "position": pos,
                **resultado
            }, ensure_ascii=False)
            yield line + "\n"

            # keep-alive a cada ~5s para evitar idle timeout em provedores
            now = asyncio.get_event_loop().time()
            if now - last_ping > 5:
                yield ':\n'  # comentário no NDJSON/SSE-style, mantém conexão
                last_ping = now

        # --- marcador de fim --- #
        yield '{"done": true}\n'

    headers = {
        "Cache-Control": "no-store, no-transform",
        "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
        "Access-Control-Allow-Credentials": "true",
        # dica para alguns CDNs
        "X-Content-Type-Options": "nosniff"
    }
    return StreamingResponse(gen(), media_type="application/x-ndjson", headers=headers)
