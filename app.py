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
        "https://souzaedgar.github.io/Sheep_AdOps_frontend",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ===== OPTIONS global =====
@app.options("/{full_path:path}")
async def preflight(full_path: str, request: Request):
    origin = request.headers.get("origin", "*")
    req_headers = request.headers.get("access-control-request-headers", "*")
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": req_headers,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400",
        }
    )
# ===== Rotas ===== #
app.include_router(main_routes.router)
