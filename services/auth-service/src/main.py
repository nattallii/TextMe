from fastapi import FastAPI
from src.api.v1.router import router as v1_router
from contextlib import asynccontextmanager
from src.messaging.rabbitmq import connect_rabbitmq, close_rabbitmq



@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_rabbitmq()
    yield
    await close_rabbitmq()


app = FastAPI(
    lifespan=lifespan,
    title="Auth Service",
    description="Auth Service",
    root_path="/auth",
    docs_url="/docs",
    openapi_url="/openapi.json",
)
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health/ready")
def ready():
    return {"status": "ready"}


@app.get("/health/live")
def live():
    return {"status": "ok"}