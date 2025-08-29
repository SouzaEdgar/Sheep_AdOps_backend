from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import main_routes
from services.url_services import init_client, close_client
from contextlib import asynccontextmanager

# ===== Lifespan (init / close) ===== #
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_client()
    yield
    await close_client()

app = FastAPI(lifespan=lifespan)

# ===== Rotas ===== #
app.include_router(main_routes.router)

# ===== CORS (habilitar) ===== #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://souzaedgar.github.io/Sheep_AdOps_frontend/"],  # localhost ou front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
