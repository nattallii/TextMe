from fastapi import FastAPI
from src.api.v1.router import router as v1_router



app = FastAPI(title="Auth Service", description="Auth Service")
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health/ready")
def ready():
    return {"status": "ready"}


@app.get("/health/live")
def live():
    return {"status": "ok"}