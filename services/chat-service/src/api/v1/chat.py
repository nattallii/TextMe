from fastapi import APIRouter, Depends, UploadFile, File
from src.db.deps import get_current_user_id
from src.services.chat import ChatService
from src.schemas.chat import CreateChat, ChatOut, ChatWithUnread, UpdateGroupSchema
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


# ── Group management ──────────────────────────────────────────────────────────

@router.patch("/{chat_id}", response_model=ChatOut)
async def update_group(
    chat_id: str,
    data: UpdateGroupSchema,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    """Rename a group chat (admin only)."""
    return await service.update_group(chat_id, user_id, data)


@router.patch("/{chat_id}/avatar", response_model=ChatOut)
async def update_group_avatar(
    chat_id: str,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    """Upload a new avatar for a group chat (admin only)."""
    return await service.update_group_avatar(chat_id, user_id, file)


@router.post("/{chat_id}/members", response_model=ChatOut, status_code=201)
async def add_member(
    chat_id: str,
    data: dict,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    """Add a member to a group chat by user_id (admin only)."""
    member_id = int(data.get("user_id", 0))
    if not member_id:
        from fastapi import HTTPException
        raise HTTPException(400, "user_id is required")
    return await service.add_member(chat_id, user_id, member_id)


@router.delete("/{chat_id}/members/{member_id}", response_model=ChatOut)
async def remove_member(
    chat_id: str,
    member_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    """Remove a member from a group chat (admin only)."""
    return await service.remove_member(chat_id, user_id, member_id)


# ── Messages ──────────────────────────────────────────────────────────────────

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


@router.post("/{chat_id}/read", status_code=204)
async def mark_chat_read(
    chat_id: str,
    user_id: int = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    """Reset unread counter for a chat (called when user is actively viewing it)."""
    await service.mark_chat_read(chat_id, user_id)