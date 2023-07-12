
from httpx import AsyncClient
from fastapi import Request, HTTPException, status
from dotenv import load_dotenv
from schemas import Role, AuthContext
import os

load_dotenv()

AUTH_URI = os.getenv('AUTH_URI')
API_KEY = os.getenv('API_KEY')


def get_token(req: Request):
    try:
        token = req.headers["Authorization"].split(" ")[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    return token


async def check_token(token: str):
    async with AsyncClient() as client:
        try:
            res = await client.post(AUTH_URI, json={'api_key': API_KEY, 'token': token})
            if res.status_code == 200:
                auth = res.json()
                return AuthContext(id=auth['id'], role=auth['role'], organization=auth['organization'])
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized")


async def check_permission(token: str, roles: tuple[Role]):
    auth = await check_token(token)
    if auth.role not in roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    return auth
