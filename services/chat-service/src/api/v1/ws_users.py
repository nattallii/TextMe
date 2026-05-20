"""
Global user-level WebSocket endpoint.

Connect once per browser session at:
    ws://host/ws/user?token=<jwt>

This socket does NOT belong to any specific chat. Its sole purpose is to
keep the user registered in `manager.user_connections` so they receive:

  - new_chat   — a new chat was created that includes them
  - new_message — a message arrived in a chat they're not currently viewing
  - unread_update — badge counts

The frontend opens this connection as soon as the user is authenticated,
regardless of which (if any) chat is active.
"""
import json
import traceback
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.ws.connection_manager import manager
from src.ws.auth import get_user_from_ws
from src.redis.client import redis_client
from src.redis.service import RedisService

redis_service = RedisService(redis_client)

router = APIRouter()


@router.websocket("/ws/user")
async def ws_user(ws: WebSocket):
    await ws.accept()

    try:
        user_id = await get_user_from_ws(ws)
        print(f"[ws/user] AUTH OK — user_id={user_id}")
    except Exception as e:
        print(f"[ws/user] AUTH FAILED — {e}")
        traceback.print_exc()
        await ws.close(code=1008)
        return

    try:
        await manager.connect_user(ws, user_id)
        print(f"[ws/user] REGISTERED — user_id={user_id}, total user_connections={dict(manager.user_connections)}")
    except Exception as e:
        print(f"[ws/user] connect_user FAILED — {e}")
        traceback.print_exc()
        await ws.close(code=1011)
        return

    try:
        await redis_service.set_online(user_id)
        print(f"[ws/user] set_online OK — user_id={user_id}")
    except Exception as e:
        # Non-fatal — keep the socket alive even if Redis fails
        print(f"[ws/user] set_online FAILED (non-fatal) — {e}")
        traceback.print_exc()

    try:
        while True:
            raw = await ws.receive_text()
            try:
                payload = json.loads(raw)
                if payload.get("type") == "ping":
                    await ws.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        print(f"[ws/user] DISCONNECTED — user_id={user_id}")
        await manager.disconnect_user(ws, user_id)
        try:
            await redis_service.set_offline(user_id)
        except Exception:
            pass
    except Exception as e:
        print(f"[ws/user] UNEXPECTED ERROR — user_id={user_id} — {e}")
        traceback.print_exc()
        await manager.disconnect_user(ws, user_id)