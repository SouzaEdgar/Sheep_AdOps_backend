import httpx
import asyncio
from utils import functions as adops

client: httpx.AsyncClient | None = None
semaforo = asyncio.Semaphore(5)
MAX_RETRIES = 3

# async def init_client():
#     global client
#     client = httpx.AsyncClient(follow_redirects=True, timeout=15.0)

# async def close_client():
#     global client
#     if client:
#         await client.aclose()
#         client = None

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
    resultados = []
    urls_validas = []

    # --- Separar URLs validas de invalidas --- #
    for url in urls:
        if adops.valid_url(url):
            tarefas.append(get_response_async(url))
            urls_validas.append(url)
        else:
            resultados.append({
                "position": len(resultados) + 1,
                "url": url,
                "params": [],
                "status": "Erro: URL inválida"
            })

    # --- Executar tarefas simultanes (requisições) --- #
    #responses = await asyncio.gather(*tarefas)

    # --- Montar Resultados --- #
    for i, future in enumerate(asyncio.as_completed(tarefas), start=len(resultados) + 1):
        resp = await future
        idx_url = i - len(resultados) - 1
        url_atual = urls_validas[idx_url]

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
                "url": url_atual,
                "params": [],
                "status": f"Erro: {resp}"
            })

    return resultados

