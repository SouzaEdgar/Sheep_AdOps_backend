from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import main_routes
from fastapi.responses import JSONResponse
# from services.url_services import init_client, close_client
# from contextlib import asynccontextmanager

# >>> Inicializar "lazy" (config para vercel) <<< #
# # ===== Lifespan (init / close) ===== #
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await init_client()
#     yield
#     await close_client()

#app = FastAPI(lifespan=lifespan)
app = FastAPI()

# ===== CORS (habilitar) ===== #
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://souzaedgar.github.io",
        "https://souzaedgar.github.io/Sheep_AdOps_frontend",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Middleware para OPTIONS / Preflight ===== #
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str, request: Request):
    headers = {
        "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Access-Control-Allow-Headers": request.headers.get("access-control-request-headers", "*"),
        "Access-Control-Allow-Credentials": "true",
    }
    return JSONResponse(status_code=200, content={}, headers=headers)

# ===== Rotas ===== #
app.include_router(main_routes.router)
