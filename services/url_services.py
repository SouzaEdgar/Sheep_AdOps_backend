import httpx
import asyncio
from utils import functions as adops
from typing import AsyncGenerator, Dict, Any, List, Tuple, Union

client: httpx.AsyncClient | None = None

# ===== Ajuste de concorrência (para Vercel) ===== #
#semaforo = asyncio.Semaphore(3) # tratar posteriormente
MAX_RETRIES = 1
TIMEOUT = httpx.Timeout(8.0)
LIMITS = httpx.Limits(max_keepalive_connections=5, max_connections=20)

async def get_client() -> httpx.AsyncClient:
    global client
    if client is None:
        client = httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT)
    return client

async def fetch_once(url: str, headers: Dict[str, str]) -> Union[httpx.Response, Exception]:
    try:
        cli = await get_client()
        return await cli.get(url, headers=headers)
    except Exception as e:
        return e

async def get_response_async(client: httpx.AsyncClient, url: str, semaforo: asyncio.Semaphore) -> Tuple[str, Union[httpx.Response, Exception]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        )
    }
    async with semaforo:
        ### Testar nova solução, evitar confusão de escopo ###
        # for attempt in range(1, MAX_RETRIES + 1):
        #     resp = await fetch_once(url, headers)
        #     if isinstance(resp, httpx.Response):
        #         return resp
        #     if attempt < MAX_RETRIES:
        #         await asyncio.sleep(0.5 * attempt)  # backoff
        # return resp  # Exception depois do último retry
        try:
            resp = await client.get(url, headers=headers, follow_redirects=True)
            return url, resp
        except Exception as e:
            return url, e

async def process_urls_stream(urls: List[str], params: List[str]) -> AsyncGenerator[Dict[str, Any], None]:
    semaforo = asyncio.Semaphore(3)

    # ===== Produz imediatamente as inválidas ===== #
    validas: List[str] = []
    for url in urls:
        if adops.valid_url(url):
            validas.append(url)
        else:
            yield {
                "url": url,
                "params": [],
                "status": "Erro: URL inválida"
            }

    # ===== Usar o context manager para garantir que o cliente feche no final do stream ===== #
    async with httpx.AsyncClient(timeout=TIMEOUT, limits=LIMITS) as client:
        tasks = [get_response_async(client, u, semaforo) for u in validas]
        
        # ===== Receber a URL e a Resposta juntas, sem precisar de loop de busca ===== #
        for fut in asyncio.as_completed(tasks):
            url_original, resp = await fut    
            if isinstance(resp, httpx.Response):
                encontrados = [
                    {"param": k, "valor": v}
                    for k, v in adops.parameters_search(str(resp.url), params)
                ]
                yield {
                    "url": str(resp.url),
                    "params": encontrados,
                    "status": resp.status_code
                }
            else:
                yield {
                    "url": url_original,
                    "params": [],
                    "status": f"Erro: {type(resp).__name__}"
                }
