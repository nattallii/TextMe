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
        await ws.close(code=1008)
        return

    try:
        await manager.connect_user(ws, user_id)
        print(f"[ws/user] REGISTERED — user_id={user_id}, total user_connections={list(manager.user_connections.keys())}")
    except Exception as e:
        print(f"[ws/user] connect_user FAILED — {e}")
        traceback.print_exc()
        await ws.close(code=1011)
        return

    try:
        await redis_service.set_online(user_id)
        print(f"[ws/user] set_online OK — user_id={user_id}")
    except Exception as e:
        print(f"[ws/user] set_online FAILED (non-fatal) — {e}")

    # 1. Send the new user the full list of currently online users
    online_ids = [uid for uid in manager.user_connections.keys() if uid != user_id]
    await ws.send_json({"type": "online_users", "data": online_ids})

    # 2. Notify all OTHER connected users that this user is now online
    await manager.broadcast_user_status(user_id, online=True)

    try:
        while True:
            raw = await ws.receive_text()
            try:
                payload = json.loads(raw)

                if payload.get("type") == "ping":
                    await ws.send_json({"type": "pong"})

                # Client requests current list of online users
                elif payload.get("type") == "get_online_users":
                    # Return all users who currently have an active connection
                    online_ids = list(manager.user_connections.keys())
                    await ws.send_json({
                        "type": "online_users",
                        "data": online_ids,
                    })

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        print(f"[ws/user] DISCONNECTED — user_id={user_id}")
        await manager.disconnect_user(ws, user_id)
        try:
            await redis_service.set_offline(user_id)
            # Notify all chat members that this user is now offline
            await manager.broadcast_user_status(user_id, online=False)
        except Exception:
            pass
    except Exception as e:
        print(f"[ws/user] UNEXPECTED ERROR — user_id={user_id} — {e}")
        traceback.print_exc()
        await manager.disconnect_user(ws, user_id)
        try:
            await redis_service.set_offline(user_id)
            await manager.broadcast_user_status(user_id, online=False)
        except Exception:
            pass