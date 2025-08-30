import httpx
import asyncio
import json
from utils import functions as adops

client: httpx.AsyncClient | None = None
semaforo = asyncio.Semaphore(5)
MAX_RETRIES = 2

# ===== Criação lazy do client ===== #
async def get_client():
    global client
    if client is None:
        client = httpx.AsyncClient(follow_redirects=True, timeout=15.0)
    return client

# ===== Requisição assincrona por URL ===== #
async def get_response_async(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/115.0 Safari/537.36"
    }
    async with semaforo:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                cli = await get_client()
                response = await cli.get(url, headers=headers)
                return response
            except httpx.RequestError as e:
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(0.5 * attempt) # realizar backoff incremental
                else:
                    return e

# ===== Processamento de URLs ===== #
async def process_urls_async(urls, params):
    tarefas = []
    urls_validas = []

    # --- URLs validas/invalidas --- #
    for url in urls:
        if adops.valid_url(url):
            tarefas.append(get_response_async(url))
            urls_validas.append(url)
        else:
            resultado = {
                "position": len(urls_validas) + 1,
                "url": url,
                "params": [],
                "status": "Erro: URL inválida"
            }
            yield json.dumps(resultado)

    # --- Montar Resultados e enviar conforme chegam--- #
    for i, future in enumerate(asyncio.as_completed(tarefas), start=len(resultados) + 1):
        resp = await future
        url_atual = urls_validas[i - 1]

        if isinstance(resp, httpx.Response):
            # --- Parametros encontrados --- #
            parametros = [{
                "param": k,
                "valor": v
            } for k, v in adops.parameters_search(str(resp.url), params)]
            # --- Formar Resultados (geral) --- #
            resultados = {
                "position": i,
                "url": str(resp.url),
                "params": parametros,
                "status": resp.status_code
            }
        else:
            # --- Formar Resultados com Erro --- #
            resultados = {
                "position": i,
                "url": url_atual,
                "params": [],
                "status": f"Erro: {resp}"
            }

    yield json.dumps(resultado)

