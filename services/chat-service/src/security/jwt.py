from fastapi import HTTPException, status
from jose import jwt, JWTError
from src.security.config import settings


def decode_token(token: str, raise_http: bool = True) -> int:
    """
    Decode a JWT token and return the user_id (sub).

    raise_http=True  → raises HTTPException (for HTTP endpoints)
    raise_http=False → raises ValueError (for WebSocket endpoints)
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        sub = payload.get("sub")
        if not sub:
            raise ValueError("no sub")
        return int(sub)
    except (JWTError, ValueError) as e:
        if raise_http:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        raise ValueError(f"Invalid token: {e}") from e