from fastapi import APIRouter, Request
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
@router.get("/verificar")
async def verificar_urls(request: Request, data: VerificarRequest):
    urls = (data.urls or [])[:MAX_URLS]
    parametros = data.parametros or []

    if not urls:
        # --- Devolve rápido se vazio --- #
        return PlainTextResponse("", status_code=204, headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*")
        })

    async def gen():
        pos = 0
        last_ping = asyncio.get_event_loop().time()

        async for resultado in process_urls_stream(urls, parametros):
            pos += 1
            yield json.dumps({"position": pos, **resultado}, ensure_ascii=False) + "\n"

            # keep-alive a cada ~5s para não fechar a conexão no Vercel
            now = asyncio.get_event_loop().time()
            if now - last_ping > 5:
                yield ":\n"
                last_ping = now

        # --- Marcador de fim --- #
        yield '{"done": true}\n'

    headers = {
        "Cache-Control": "no-store",
        "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
        "Access-Control-Allow-Credentials": "true",
        "Content-Type": "application/x-ndjson; charset=utf-8",
        "Connection": "keep-alive",
        "Transfer-Encoding": "chunked",
    }
    return StreamingResponse(gen(), media_type="application/x-ndjson", headers=headers)
