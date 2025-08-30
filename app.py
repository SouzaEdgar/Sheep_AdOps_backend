from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import main_routes
from fastapi.responses import StreamingResponse


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

# ===== Rotas ===== #
app.include_router(main_routes.router)
