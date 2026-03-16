from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import main_routes
from fastapi.responses import JSONResponse


app = FastAPI()

# ===== CORS (habilitar) ===== #
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://souzaedgar.github.io",
        "https://souzaedgar.github.io/",
        #"http://127.0.0.1:5500",
        #"http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ===== Rotas ===== #
app.include_router(main_routes.router)
