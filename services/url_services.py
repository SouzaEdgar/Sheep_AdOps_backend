import httpx
import asyncio
from utils import functions as adops
from typing import AsyncGenerator, Dict, Any, List, Tuple, Union

semaforo = asyncio.Semaphore(6)
MAX_RETRIES = 2
TIMEOUT = httpx.Timeout(15.0)

async def get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT)

async def fetch_once(url: str, headers: Dict[str, str]) -> Union[httpx.Response, Exception]:
    try:
        async with await get_client() as cli:
            return await cli.get(url, headers=headers)
    except Exception as e:
        return e

async def get_response_async(url: str) -> Union[httpx.Response, Exception]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        )
    }
    async with semaforo:
        for attempt in range(1, MAX_RETRIES + 1):
            resp = await fetch_once(url, headers)
            if isinstance(resp, httpx.Response):
                return resp
            if attempt < MAX_RETRIES:
                await asyncio.sleep(0.5 * attempt)
        return resp  # Exception depois do último retry

async def process_urls_stream(urls: List[str], params: List[str]) -> AsyncGenerator[Dict[str, Any], None]:
    validas: List[str] = []
    for url in urls:
        if adops.valid_url(url):
            validas.append(url)
        else:
            yield {"url": url, "params": [], "status": "Erro: URL inválida"}

    tasks: List[Tuple[str, "asyncio.Task[Union[httpx.Response, Exception]]"]] = []
    loop = asyncio.get_event_loop()
    for u in validas:
        tasks.append((u, loop.create_task(get_response_async(u))))

    if not tasks:
        return

    for fut in asyncio.as_completed([t for _, t in tasks]):
        url_atual = None
        for u, t in tasks:
            if t is fut:
                url_atual = u
                break
        resp = await fut

        if isinstance(resp, httpx.Response):
            encontrados = [
                {"param": k, "valor": v}
                for k, v in adops.parameters_search(str(resp.url), params)
            ]
            yield {"url": str(resp.url), "params": encontrados, "status": resp.status_code}
        else:
            yield {"url": url_atual or "", "params": [], "status": f"Erro: {resp}"}

