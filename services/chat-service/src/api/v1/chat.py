from fastapi import APIRouter, Depends
from src.db.deps import get_current_user_id
from src.services.chat import ChatService
from src.schemas.chat import CreateChat, ChatOut, ChatWithUnread
from src.schemas.message import MessageCreate, MessageOut

router = APIRouter(prefix="/chat", tags=["chat"])

service = ChatService()


@router.post("/", response_model=ChatOut, status_code=201)
async def create_chat(
    data: CreateChat,
    user_id: int = Depends(get_current_user_id),
):
    return await service.create_chat(user_id, data)


@router.get("/", response_model=list[ChatWithUnread])
async def get_my_chats(
    user_id: int = Depends(get_current_user_id),
):
    return await service.get_my_chats(user_id)


@router.post("/{chat_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(
    chat_id: str,
    data: MessageCreate,
    user_id: int = Depends(get_current_user_id),
):
    return await service.send_message(chat_id, user_id, data)


@router.get("/{chat_id}/messages", response_model=list[MessageOut])
async def get_history(
    chat_id: str,
    user_id: int = Depends(get_current_user_id),
):
    return await service.get_history(chat_id, user_id)