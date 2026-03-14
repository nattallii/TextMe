from fastapi import WebSocket



class ConnectionManager:
    def __init__(self):
        self.active: dict[str, set[WebSocket]] = {}


    async def connect(self, ws: WebSocket, user_id: str):
        await ws.accept()
        self.active.setdefault(user_id, set()).add(ws)

    async def disconnect(self, ws: WebSocket, user_id: str):
        if user_id in self.active:
            self.active[user_id].discard(ws)
            if not self.active[user_id]:
                del self.active[user_id]


    async def send_to_user(self, user_id: str, payload: dict) -> bool:
        sockets = list(self.active.get(user_id, []))
        if not sockets:
            return False

        for s in sockets:
            await s.send_json(payload)
        return True


    async def broadcast(self, user_ids: list[str], payload: dict,):
        for user_id in user_ids:
            await self.send_to_user(user_id, payload)




