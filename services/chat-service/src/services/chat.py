from fastapi import HTTPException, status
from src.repository.message import MessageRepository
from src.repository.chat import ChatRepository
from src.models.chat import ChatReadState, ChatPermissionModel, Chat
from src.schemas.message import MessageCreate, MessageOut
from src.schemas.chat import CreateChat, ChatOut, ChatType



class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()
        self.message_repository = MessageRepository()

    async def create_chat(self, user_id: int, data: CreateChat) -> ChatOut:

        if data.type == ChatType.PRIVATE:
            if len(data.member_ids) != 1:
                raise HTTPException(400, "Private chat must have exactly 1 member")

            member_id = data.member_ids[0]

            if user_id == member_id:
                raise HTTPException(400, "Cannot create chat with self")

            existing_chat = await self.chat_repository.get_by_members(user_id, member_id)
            if existing_chat:
                return ChatOut(
                    id=str(existing_chat.id),
                    type=existing_chat.type,
                    members=existing_chat.members,
                    created_by=existing_chat.created_by,
                    created_at=existing_chat.created_at
                )

            members = [user_id, member_id]

        elif data.type == ChatType.GROUP:
            if not data.member_ids:
                raise HTTPException(400, "Group must have members")

            members = list(set([user_id] + data.member_ids))

        else:
            raise HTTPException(400, "Invalid chat type")

        chat = await self.chat_repository.create(
            members=members,
            type=data.type,
            name=data.name,
            created_by=user_id
        )

        for m in members:
            await ChatPermissionModel(
                chat_id=chat.id,
                user_id=m,
                can_send_messages=True
            ).insert()

        for m in members:
            await ChatReadState(chat_id=chat.id, user_id=m).insert()

        return ChatOut(
            id=str(chat.id),
            type=chat.type,
            name=chat.name,
            members=chat.members,
            created_by=chat.created_by,
            created_at=chat.created_at
        )

    async def send_message(self, chat_id: str, user_id: int, data: MessageCreate) -> MessageOut:
        chat = await self.chat_repository.get_by_id(chat_id)

        if not chat:
            raise HTTPException(404, "Chat not found")

        if user_id not in chat.members:
            raise HTTPException(403, "Not a member")

        perm = await ChatPermissionModel.find_one({
            "chat_id": chat_id,
            "user_id": user_id,
        })

        if perm and not perm.can_send_messages:
            raise HTTPException(403, "User not allowed")

        message = await self.message_repository.create(
            chat_id=chat_id,
            sender_id=user_id,
            content=data.content
        )

        chat.last_message = message.content
        chat.last_message_at = message.created_at
        chat.updated_at = message.created_at

        await chat.save()

        return MessageOut(
            id=str(message.id),
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            content=message.content,
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
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ]



    async def get_my_chats(self, user_id: int) -> list[dict]:
        chats = await self.chat_repository.get_user_chats(user_id)

        result = []

        for c in chats:
            state = await ChatReadState.find_one({
                "chat_id": c.id,
                "user_id": user_id
            })

            unread = 0
            if state and state.last_read_message_id:
                unread = await self.message_repository.count_after(
                    c.id, state.last_read_message_id
                )

            result.append({
                **self._to_chat_out(c).dict(),
                "unread_count": unread
            })

        return result

    def _to_chat_out(self, chat):
        return ChatOut(
            id=str(chat.id),
            type=chat.type,
            name=chat.name,
            members=chat.members,
            last_message=chat.last_message,
            last_message_at=chat.last_message_at,
            created_by=chat.created_by,
            created_at=chat.created_at,
            updated_at=chat.updated_at
        )