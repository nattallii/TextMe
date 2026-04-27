from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from src.security.config import settings
from beanie import init_beanie
from src.models.message import Message
from src.models.chat import Chat, ChatPermissionModel, ChatReadState

async def init_db(app: FastAPI):
    client = AsyncIOMotorClient(settings.MONGO_URL)
    app.state.db = client[settings.MONGO_DB]
    await init_beanie(
        database=client[settings.MONGO_DB],
        document_models=[
            Chat,
            Message,
            ChatPermissionModel,
            ChatReadState,
        ],
    )
