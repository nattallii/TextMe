from fastapi import HTTPException
from src.models.message import Message
from src.models.chat import ChatPermissionModel
class MessageRepository:

    async def create(self, chat_id: str, sender_id: int, content: str) -> Message:
        message = Message(chat_id=chat_id, sender_id=sender_id, content=content)
        await message.insert()
        return message



    async def get_by_chat_id(self, chat_id: int) -> list[Message]:
        return await Message.find({"chat_id": chat_id}).sort(+Message.created_at).to_list()

    async def count_after(self, chat_id: str, last_id: str) -> int:
        return await Message.find({"chat_id": chat_id, "id":  {"$gt": last_id}}).count()


    async def delete_message(self, chat_id: str, message_id: str, user_id: int) -> Message | None:
        message = await Message.find_one({
            "chat_id": chat_id,
            "id": message_id
        })

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
