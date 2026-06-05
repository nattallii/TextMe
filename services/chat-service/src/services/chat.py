import httpx
from fastapi import HTTPException
from src.repository.message import MessageRepository
from src.repository.chat import ChatRepository
from src.models.message import Message
from src.models.chat import ChatReadState, ChatPermissionModel, Chat
from src.schemas.message import MessageCreate, MessageOut, MessageUpdate
from src.schemas.chat import CreateChat, ChatOut, ChatType
from src.ws.schemas import NewMessageData
from src.ws.connection_manager import manager
from src.redis.service import RedisService
from src.redis.client import redis_client
import os

redis_service = RedisService(redis_client)

# Profile service base URL — configurable via env
PROFILE_SERVICE_URL = os.getenv("PROFILE_SERVICE_URL", "http://profile:8000")


async def get_user_info(user_id: int) -> dict | None:
    """Fetch basic user info from the profile service."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{PROFILE_SERVICE_URL}/api/v1/users/{user_id}")
            if r.status_code == 200:
                return r.json()
    except Exception as e:
        print(f"[get_user_info] failed for user_id={user_id}: {e}")
    return None


async def enrich_members(member_ids: list[int]) -> list[dict]:
    """Return a list of member info dicts for the given IDs."""
    import asyncio
    results = await asyncio.gather(*[get_user_info(uid) for uid in member_ids])
    enriched = []
    for uid, info in zip(member_ids, results):
        if info:
            enriched.append({
                "id": uid,
                "username": info.get("username"),
                "phone": info.get("phone"),
                "avatar_url": info.get("avatar_url"),
            })
        else:
            enriched.append({"id": uid, "username": None, "phone": None, "avatar_url": None})
    return enriched


class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()
        self.message_repository = MessageRepository()

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
            content=data.content,
        )

        message.delivered_to = [user_id]
        message.read_by = [user_id]

        for member in chat.members:
            if member != user_id:
                if await redis_service.is_online(member):
                    message.delivered_to.append(member)

                # Check if this member is actively viewing the chat room right now.
                # If yes — don't increment Redis so reload shows 0.
                member_in_chat = manager.is_user_in_chat(member, chat_id)

                if not member_in_chat:
                    await redis_service.increment_unread(member, chat_id)

                count = await redis_service.get_unread(member, chat_id)
                await manager.send_unread_update(chat_id, member, count)

        await message.save()

        await manager.send_new_message(
            NewMessageData(
                id=str(message.id),
                chat_id=str(chat_id),
                sender_id=user_id,
                content=message.content,
                created_at=message.created_at,
            ),
            member_ids=chat.members,
        )

        await manager.send_message_status(
            chat_id,
            str(message.id),
            message.delivered_to,
            message.read_by,
        )

        await redis_service.publish(
            "chat_events",
            {
                "type": "new_message",
                "chat_id": chat_id,
                "data": {
                    "id": str(message.id),
                    "chat_id": chat_id,
                    "sender_id": user_id,
                    "content": message.content,
                },
            },
        )

        chat.last_message = message.content
        chat.last_message_at = message.created_at
        chat.updated_at = message.created_at
        await chat.save()

        return MessageOut.model_validate(message)

    async def update_message(self, chat_id: str, message_id: str, data: MessageUpdate, user_id: int):
        message = await self.message_repository.update_message(
            chat_id=chat_id,
            user_id=user_id,
            message_id=message_id,
            content=data.content,
        )
        if not message:
            raise HTTPException(404, "Message not found")
        return message

    async def delete_message(self, chat_id: str, message_id: str, user_id: int):
        message = await self.message_repository.delete_message(chat_id, message_id, user_id)
        if not message:
            raise HTTPException(404, "Message not found")
        return MessageOut.model_validate(message)

    async def update_group(self, chat_id: str, user_id: int, data):
        """Rename a group chat. Only admin (created_by) can do this."""
        chat = await self.chat_repository.get_by_id(chat_id)
        if not chat:
            raise HTTPException(404, "Chat not found")
        if chat.type != "group":
            raise HTTPException(400, "Not a group chat")
        if chat.created_by != user_id:
            raise HTTPException(403, "Only admin can rename the group")
        if data.name:
            chat.name = data.name.strip()
            await chat.save()
        return chat

    async def update_group_avatar(self, chat_id: str, user_id: int, file):
        """Upload group avatar directly to MinIO (same as upload service does)."""
        import uuid, io
        from src.services.minio import client as minio_client

        chat = await self.chat_repository.get_by_id(chat_id)
        if not chat:
            raise HTTPException(404, "Chat not found")
        if chat.type != "group":
            raise HTTPException(400, "Not a group chat")
        if chat.created_by != user_id:
            raise HTTPException(403, "Only admin can change the avatar")

        ALLOWED = {"image/png", "image/jpeg", "image/webp", "image/gif"}
        if file.content_type not in ALLOWED:
            raise HTTPException(400, "Only images are allowed for group avatar")

        file_bytes = await file.read()
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "File too large (max 10 MB)")

        object_name = f"{uuid.uuid4()}-{file.filename}"

        try:
            minio_client.put_object(
                bucket_name="chat-files",
                object_name=object_name,
                data=io.BytesIO(file_bytes),
                length=len(file_bytes),
                content_type=file.content_type,
            )
        except Exception as e:
            print(f"[update_group_avatar] MinIO error: {e}")
            raise HTTPException(500, "Failed to upload avatar")

        url = f"http://localhost:9000/chat-files/{object_name}"
        chat.avatar_url = url
        await chat.save()
        return chat

    async def add_member(self, chat_id: str, user_id: int, member_user_id: int):
        """Add a member to a group chat by user_id. Admin only."""
        chat = await self.chat_repository.get_by_id(chat_id)
        if not chat:
            raise HTTPException(404, "Chat not found")
        if chat.type != "group":
            raise HTTPException(400, "Not a group chat")
        if chat.created_by != user_id:
            raise HTTPException(403, "Only admin can add members")
        if member_user_id in chat.members:
            raise HTTPException(409, "User is already a member")

        chat.members.append(member_user_id)
        await chat.save()

        # Notify new member via WS
        await manager.send_new_chat(chat)
        return chat

    async def remove_member(self, chat_id: str, user_id: int, member_id: int):
        """Remove a member from a group chat. Admin only."""
        chat = await self.chat_repository.get_by_id(chat_id)
        if not chat:
            raise HTTPException(404, "Chat not found")
        if chat.type != "group":
            raise HTTPException(400, "Not a group chat")
        if chat.created_by != user_id:
            raise HTTPException(403, "Only admin can remove members")
        if member_id == chat.created_by:
            raise HTTPException(400, "Cannot remove the admin")
        if member_id not in chat.members:
            raise HTTPException(404, "User is not a member")

        chat.members.remove(member_id)
        await chat.save()

        # Reset unread for removed member
        await redis_service.reset_unread(member_id, chat_id)

        return chat

    async def delete_chat(self, chat_id: str, user_id: int):
        chat = await self.chat_repository.delete_chat(chat_id, user_id)
        if not chat:
            raise HTTPException(404, "Chat not found")
        return ChatOut.model_validate(chat)

    async def leave_chat(self, chat_id: str, user_id: int):
        chat = await self.chat_repository.get_by_id(chat_id)

    async def create_chat(self, user_id: int, data: CreateChat):
        if data.type == ChatType.PRIVATE:
            return await self.create_private_chat(user_id, data.member_ids)
        if data.type == ChatType.GROUP:
            return await self.create_group_chat(user_id, data.member_ids, data.name)

    async def create_private_chat(self, user_id: int, member_ids: list[int]):
        other_user = member_ids[0]
        members = sorted([user_id, other_user])

        # Only reuse a chat that is not deleted AND the current user hasn't hidden it.
        # "hidden_for" is set when a user "deletes" a private chat from their side —
        # in that case we must create a fresh chat with no old messages.
        existing = await Chat.find_one(
            Chat.members == members,
            Chat.type == "private",
            Chat.is_deleted == False,          # noqa: E712 — group chats hard-delete
            {"hidden_for": {"$ne": user_id}},  # not hidden by current user
        )
        if existing:
            return existing

        chat = Chat(members=members, type="private", created_by=user_id)
        await chat.insert()
        await manager.send_new_chat(chat)
        return chat

    async def create_group_chat(self, user_id: int, member_ids: list[int], name: str):
        members = list(set(member_ids + [user_id]))
        chat = Chat(members=members, type="group", name=name, created_by=user_id)
        await chat.insert()
        await manager.send_new_chat(chat)
        return chat

    async def mark_chat_read(self, chat_id: str, user_id: int) -> None:
        """Reset unread counter in Redis. Called when user is actively viewing a chat."""
        await redis_service.reset_unread(user_id, chat_id)

    async def get_history(self, chat_id: str, user_id: int):
        chat = await self.chat_repository.get_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        if user_id not in chat.members:
            raise HTTPException(status_code=403, detail="Access denied")
        return await self.message_repository.get_by_chat_id(chat_id)

    async def get_my_chats(self, user_id: int) -> list[dict]:
        chats = await self.chat_repository.get_user_chats(user_id)

        # Collect all unique member IDs across all chats
        all_member_ids = list({m for c in chats for m in c.members})
        members_info = await enrich_members(all_member_ids)
        # Build a lookup map: user_id -> info dict
        members_map = {info["id"]: info for info in members_info}

        result = []
        for c in chats:
            unread = await redis_service.get_unread(user_id, str(c.id))
            chat_dict = self._to_chat_out(c).dict()
            # Attach enriched member info so the frontend can display
            # names/avatars even for users not in the contact list
            chat_dict["members_info"] = [
                members_map.get(mid, {"id": mid, "username": None, "phone": None, "avatar_url": None})
                for mid in c.members
            ]
            chat_dict["unread_count"] = unread
            result.append(chat_dict)

        return result

    async def mark_as_read(self, message_id: str, user_id: int) -> None:
        message = await Message.find_one({"id": message_id})
        if not message:
            return

        state = await ChatReadState.find_one({"chat_id": message.chat_id, "user_id": user_id})
        if not state:
            return

        state.last_read_message_id = message.id
        await state.save()

        if user_id not in message.read_by:
            message.read_by.append(user_id)
            await message.save()

        await redis_service.reset_unread(user_id, message.chat_id)
        await manager.send_message_status(
            message.chat_id, str(message.id), message.delivered_to, message.read_by
        )

    async def get_chat(self, chat_id: str, user_id: int):
        chat = await Chat.get(chat_id)
        if not chat:
            raise HTTPException(404, "Chat not found")
        if user_id not in chat.members:
            raise HTTPException(403, "Forbidden")
        return chat

    def _to_chat_out(self, chat):
        return ChatOut(
            id=str(chat.id),
            type=chat.type,
            name=chat.name,
            members=chat.members,
            avatar_url=getattr(chat, "avatar_url", None),
            last_message=chat.last_message,
            last_message_at=chat.last_message_at,
            created_by=chat.created_by,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            is_deleted=chat.is_deleted,
        )