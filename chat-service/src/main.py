from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.db.mongo import init_db
from src.api.v1.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(app)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Chat Service",
    description="Chat Service",
    root_path="/chat",
    docs_url="/docs",
    openapi_url="/openapi.json",
)
app.include_router(chat_router, prefix="/api/v1")

@app.get("/health/ready")
def ready():
    return {"status": "ready"}


@app.get("/health/live")
def live():
    return {"status": "ok"}
