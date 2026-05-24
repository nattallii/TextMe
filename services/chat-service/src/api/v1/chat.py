from fastapi import APIRouter, Depends, UploadFile, File
from src.db.deps import get_current_user_id
from src.services.chat import ChatService
from src.schemas.chat import CreateChat, ChatOut, ChatWithUnread
from src.schemas.message import MessageCreate, MessageOut, MessageUpdate

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service():
    return ChatService()


@router.post("/", response_model=ChatOut, status_code=201)
async def create_chat(
    data: CreateChat,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    return await service.create_chat(user_id, data)


@router.get("/", response_model=list[ChatWithUnread])
async def get_my_chats(
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    return await service.get_my_chats(user_id)



@router.get("/{chat_id}", response_model=ChatOut)
async def get_chat(
    chat_id: str,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    return await service.get_chat(chat_id, user_id)


@router.post("/{chat_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(
    chat_id: str,
    data: MessageCreate,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    return await service.send_message(chat_id, user_id, data)


@router.get("/{chat_id}/history", response_model=list[MessageOut])
async def get_history(
    chat_id: str,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    return await service.get_history(chat_id, user_id)


@router.post("/messages/{message_id}/read", status_code=204)
async def mark_as_read(
    message_id: str,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    await service.mark_as_read(message_id, user_id)


@router.patch("/{chat_id}/messages/{message_id}", response_model=MessageOut)
async def edit_message(
    chat_id: str,
    message_id: str,
    data: MessageUpdate,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    return await service.update_message(chat_id, message_id, data, user_id)


@router.delete("/{chat_id}/messages/{message_id}", response_model=MessageOut)
async def delete_message(
    chat_id: str,
    message_id: str,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    return await service.delete_message(chat_id, message_id, user_id)


@router.delete("/{chat_id}", response_model=ChatOut)
async def delete_chat(
        chat_id: str,
        user_id: int = Depends(get_current_user_id),
        service: ChatService = Depends(get_chat_service)
):
    return await service.delete_chat(chat_id, user_id)






