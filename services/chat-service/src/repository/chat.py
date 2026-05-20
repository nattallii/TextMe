from beanie.operators import In
from fastapi import HTTPException
from src.models.chat import Chat


class ChatRepository:

    async def create(self, members, type, name, created_by):
        chat = Chat(
            members=list(set(members)),
            type=type,
            name=name,
            created_by=created_by
        )
        await chat.insert()
        return chat

    async def get_private_chat(self, members: list[int]):
        return await Chat.find_one(
            Chat.members == members,
            Chat.type == "private"
        )




    async def get_by_id(self, chat_id: str) -> Chat | None:
        return await Chat.get(chat_id)


    async def get_by_members(self, user1: int, user2: int) -> Chat | None:
        return await Chat.find_one({
            "type": "private",
            "members": {"$all": [user1, user2]},
            "members.2": {"$exists": False}
        })

    async def get_user_chats(self, user_id: int) -> list[Chat]:
        return await Chat.find(
            {
                "members": user_id,
                "hidden_for": {"$ne": user_id},
                "is_deleted": {"$ne": True},
            }
        ).to_list()

    async def add_member(self, chat_id: str, member_id: int) -> None:
        chat = await Chat.get(chat_id)

        if not chat:
            return

        if member_id not in chat.members:
            chat.members.append(member_id)
            await chat.save()


    async def remove_member(self, chat_id: str, member_id: int) -> None:

        chat = await Chat.get(chat_id)
        if not chat:
            return

        if member_id in chat.members:
            chat.members.remove(member_id)
            await chat.save()

    async def left_chat(
            self,
            chat_id: str,
            user_id: int
    ) -> Chat | None:

        chat = await Chat.get(chat_id)

        if not chat:
            return None

        if user_id not in chat.members:
            raise HTTPException(403, "Not a member of this chat")

        if chat.type == "private":
            raise HTTPException(
                400,
                "Cannot leave private chat"
            )

        chat.members.remove(user_id)

        if user_id == chat.created_by:

            if chat.members:
                chat.created_by = chat.members[0]

            else:
                chat.is_deleted = True

        await chat.save()

        return chat


    async def delete_chat(self, chat_id: str, user_id: int) -> Chat | None:
        chat = await Chat.get(chat_id)
        if not chat:
            return

        if user_id not in chat.members:
            raise HTTPException(403, "Action denied")

        if chat.type == "private":

            if user_id not in chat.hidden_for:
                chat.hidden_for.append(user_id)

            await chat.save()
            return chat

        if chat.type == "group":
            if chat.created_by == user_id:
                chat.is_deleted = True

                await chat.save()
                return chat
        chat.members.remove(user_id)
        await chat.save()
        return chat





    async def change_title(self, chat_id: str, title: str) -> None:
        chat = await Chat.get(chat_id)
        if not chat:
            return

        if chat.type != "group":
            raise HTTPException(400, "Only group chats can have title")

        chat.title = title
        await chat.save()
