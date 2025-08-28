import httpx
import asyncio
from utils import functions as adops

client: httpx.AsyncClient | None = None
semaforo = asyncio.Semaphore(10)

async def init_client():
    global client
    client = httpx.AsyncClient(follow_redirects=True, timeout=15.0)

async def close_client():
    global client
    if client:
        await client.aclose()
        client = None

async def get_response_async(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/115.0 Safari/537.36"
    }
    global client
    async with semaforo:
        try:
            response = await client.get(url, headers=headers)
            return response
        except httpx.RequestError as e:
            return e

async def process_urls_async(urls, params):
    tarefas = []
    resultados = []
    urls_validas = []

    for url in urls:
        if adops.valid_url(url):
            tarefas.valid_url(url)
            urls_validas.append(url)
        else:
            resultados.append({
                "position": len(resultados) + 1,
                "url": url,
                "params": [],
                "status": "Erro: URL inválida"
            })
    
    responses = await asyncio.gather(*tarefas)

    for i, resp in enumerate(responses, start=len(resultados) + 1):
        if isinstance(resp, httpx.Response):
            # --- Parametros encontrados --- #
            parametros = [{
                "param": k,
                "valor": v
            } for k, v in adops.parameters_search(str(resp.url), params)]
            # --- Formar Resultados (geral) --- #
            resultados.append({
                "position": i,
                "url": str(resp.url),
                "params": parametros,
                "status": resp.status_code
            })
        else:
            # --- Formar Resultados com Erro --- #
            resultados.append({
                "position": i,
                "url": urls_validas[i - len(resultados) - 1],
                "params": "",
                "status": f"Erro: {resp}"
            })

        return resultados

