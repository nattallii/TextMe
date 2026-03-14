from beanie.operators import In
from src.models.chat import Chat


class ChatRepository:
    async def create(self, members: list[int]) -> Chat:
        chat = Chat(members=members)
        await chat.insert()
        return chat


    async def get_by_id(self, chat_id: int) -> Chat | None:
        return await Chat.get(chat_id)


    async def get_by_members(self, user1: int, user2: int) -> Chat | None:
        return await Chat.find_one({"members": {"$all": [user1, user2]}})

    async def get_user_chats(self, user_id: int) -> list[Chat]:
        return await Chat.find({"members": user_id}).to_list()