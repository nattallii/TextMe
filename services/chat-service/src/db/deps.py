from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from src.security.jwt import decode_token
from starlette import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_db(request: Request):
    return request.app.state.db

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    print(f"TOKEN: {token}")
    try:
        return decode_token(token)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})