import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.mongo import init_db
from src.api.v1.chat import router as chat_router
from src.api.v1.upload import router as upload_router
from src.api.v1.ws import router as ws_router
from src.api.v1.ai import router as ai_router
from src.api.v1.ws_users import router as ws_users_router
from src.api.v1.contacts import router as contacts_router
from src.redis.listener import redis_listener
from src.redis.client import redis_client
from src.redis.service import RedisService

redis_service = RedisService(redis_client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis_client
    await init_db(app)
    asyncio.create_task(redis_listener())
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Chat Service",
    description="Chat Service",
    root_path="/chat",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Single CORS middleware — no custom middleware needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(contacts_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(ws_router)
app.include_router(ws_users_router)


@app.get("/health/ready")
def ready():
    return {"status": "ready"}


@app.get("/health/live")
def live():
    return {"status": "ok"}