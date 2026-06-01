# AdOps Helper - API
  
API assíncrona desenvolvida para automatizar e otimizar os processos de QA em operações AdOps.

O front-end da aplicação foi separado e possui deploy independente através do GitHub Pages, consumindo os endpoints em tempo real.
https://souzaedgar.github.io/AdOps_Helper/

A arquitetura utiliza streaming de dados para enviar os resultados ao client assim que cada URL é resolvida, eliminando a espera pelo processamento completo do lote.



## Tecnologias Utilizadas

* **FastAPI:** Framework web assíncrono.
* **Asyncio & HTTPX:** Motor de requisições HTTP. Uso de `asyncio.Semaphore` para controle de concorrência, evitando gargalos de rede.
* **Server-Sent Events (Streaming Response):** Implementação de respostas em fluxo (`application/x-ndjson`) com técnicas de anti-buffering para entrega contínua.
* **Vercel Serverless:** Configuração nativa (`vercel.json`) para deploy em arquitetura serverless escalável.

## Documentação da API

### `POST /verificar`

Processa uma lista de URLs e verifica a presença dos parâmetros especificados na URL de destino final.

#### Request Body
```json
{
  "urls": [
    "http://encurtador.exemplo/campanha1",
    "http://encurtador.exemplo/campanha2"
  ],
  "parametros": ["utm_source", "utm_campaign", "aff_id"]
}
```

#### Response (`application/x-ndjson`)
O endpoint retorna um stream de dados onde cada linha representa o resultado do processamento de uma URL ou o status final da requisição.

```json
{"position": 1, "url": "https://sitefinal.com.br/landing?utm_source=facebook", "params": [{"param": "utm_source", "valor": "facebook"}], "status": 200}
{"position": 2, "url": "https://sitefinal.com.br/landing?utm_source=google", "params": [{"param": "utm_source", "valor": "google"}], "status": 200}
{"done": true}
```

## Instalação e Execução Local

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Sheep_AdOps_backend.git
cd Sheep_AdOps_backend
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o servidor de desenvolvimento:
```bash
uvicorn app:app --reload
```

A API estará rodando em `http://127.0.0.1:8000`. A documentação interativa (Swagger UI) pode ser acessada em `http://127.0.0.1:8000/docs`.

---
