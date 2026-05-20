from datetime import datetime, timezone

from fastapi import HTTPException
from src.models.message import Message
from src.models.chat import ChatPermissionModel


class MessageRepository:

    async def create(self, chat_id: str, sender_id: int, content: str) -> Message:
        message = Message(chat_id=chat_id, sender_id=sender_id, content=content)
        await message.insert()
        return message



    async def get_by_chat_id(self, chat_id: str) -> list[Message]:
        return await Message.find(
            Message.chat_id == chat_id
        ).sort("created_at").to_list()


    async def count_after(self, chat_id: str, last_created_at: datetime) -> int:
        return await Message.find(
            Message.chat_id == chat_id,
            Message.created_at > last_created_at
        ).count()


    async def delete_message(self, chat_id: str, message_id: str, user_id: int) -> Message | None:
        message = await Message.find_one(Message.id == message_id)

        if not message:
            return None

        if message.sender_id != user_id:
            perm = await ChatPermissionModel.find_one({
                "chat_id": chat_id,
                "user_id": user_id
            })

            if not perm or not perm.can_remove_other_messages:
                raise HTTPException(
                    status_code=403,
                    detail="Cannot delete other messages"
                )

        message.is_deleted = True
        await message.save()

        return message

    async def update_message(self, chat_id: str, message_id: str, content: str, user_id: int) -> Message | None:
        message = await Message.find_one(Message.id == message_id)
        if not message:
            return None

        if message.sender_id != user_id:
            raise HTTPException(status_code=403, detail="Cannot update other messages")

        if message.is_deleted:
            raise HTTPException(status_code=400, detail="Cannot update deleted messages")

        message.content = content
        message.is_edited = True
        message.updated_at = datetime.now(timezone.utc)
        await message.save()
        return message