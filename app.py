from fastapi import FastAPI
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

