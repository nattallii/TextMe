from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.v1.profile import router as profile_router
from src.api.v1.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware
from src.messaging.rabbitmq import connect_rabbitmq, close_rabbitmq
from src.messaging.consumer import start_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_rabbitmq()
    await start_consumer()
    yield
    await close_rabbitmq()


app = FastAPI(
    lifespan=lifespan,
    title="Profile Service",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health/ready")
def ready():
    return {"status": "ready"}


@app.get("/health/live")
def live():
    return {"status": "ok"}
