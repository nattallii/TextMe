from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.db.mongo import init_db
from src.api.v1.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(app)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "OK"}
