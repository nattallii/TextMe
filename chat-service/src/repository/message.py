from src.models.message import Message

class MessageRepository:

    async def create(self, chat_id: int, sender_id: int, text: str) -> Message:
        message = Message(chat_id=chat_id, sender_id=sender_id, text=text)
        await message.insert()
        return message



    async def get_by_chat_id(self, chat_id: int) -> list[Message]:
        return await Message.find({"chat_id": chat_id}).sort(+Message.created_at).to_list()