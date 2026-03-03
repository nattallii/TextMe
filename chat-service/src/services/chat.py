from fastapi import HTTPException, status
from src.repository.message import MessageRepository
from src.repository.chat import ChatRepository
from src.schemas.message import MessageCreate, MessageOut
from src.schemas.chat import CreateChat, ChatOut



class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()
        self.message_repository = MessageRepository()


    async def create_chat(self, user_id: int, data: CreateChat) -> ChatOut:
        if user_id == data.member_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cannot create chat with self")

        existing_chat = await self.chat_repository.get_by_members(user_id, data.member_id)
        if existing_chat:
            return ChatOut(id=str(existing_chat.id), members=existing_chat.members, created_at=existing_chat.created_at)

        chat = await self.chat_repository.create(members=[user_id, data.member_id])
        return ChatOut(id=str(chat.id), members=chat.members, created_at=chat.created_at)


    async def send_message(self, chat_id: str, user_id: int, data: MessageCreate) -> ChatOut:
        chat = await self.chat_repository.get_by_id(chat_id)

        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        if user_id not in chat.members:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")

        message = await self.message_repository.create(chat_id=chat_id, sender_id=user_id, text=data.text)

        return MessageOut(
                    id=str(message.id),
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    text=message.text,
                    is_read=message.is_read,
                    created_at=message.created_at,
                )


    async def get_history(self, chat_id: str, user_id: int) -> list[MessageOut]:
        chat = await self.chat_repository.get_by_id(chat_id)

        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        if user_id not in chat.members:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

        messages = await self.message_repository.get_by_chat_id(chat_id)
        return [
            MessageOut(
                id=str(m.id),
                chat_id=m.chat_id,
                sender_id=m.sender_id,
                text=m.text,
                is_read=m.is_read,
                created_at=m.created_at,
            )
            for m in messages
        ]

    async def get_my_chats(self, user_id: int) -> list[ChatOut]:
        chats = await self.chat_repository.get_user_chats(user_id)
        return [
            ChatOut(id=str(c.id), members=c.members, created_at=c.created_at)
            for c in chats
        ]