from fastapi import WebSocket
from src.security.jwt import decode_token


async def get_user_from_ws(ws: WebSocket) -> int:
    token = ws.query_params.get("token")

    if not token:
        raise ValueError("token is missing")

    # raise_http=False → raises ValueError instead of HTTPException
    # so WebSocket handler can catch it cleanly
    return decode_token(token, raise_http=False)