from httpx import AsyncClient
from fastapi import Request,HTTPException, status

AUTHN_URI = 'http://127.0.0.1:50501/authn/abc12345'
AUTHZ_URI = 'http://127.0.0.1:50501/authz/abc12345'

def get_token(req: Request):
    try:
        token = req.headers["Authorization"].split(" ")[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    return token

async def check_token(token:str):
    async with AsyncClient() as client:
        try:
            res = await client.post(AUTHN_URI,json={'token':token})
            if res.json()['success']:
                return
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR1")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized")


async def check_permission(token: str, roles):
    async with AsyncClient() as client:
        try:
            res = await client.post(AUTHZ_URI,json={'token':token,'roles':roles.value})
            res = res.json()
            print(res)
            if res['success']:
                return res['role']
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR2")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized"
    )