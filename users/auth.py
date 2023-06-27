import bcrypt
from pydantic import BaseModel
from fastapi import status, HTTPException, Request
from schemas import Role, Session, AuthContext
from models import get_user_by_id, get_user_by_email, User, check_email_username_inuse
import uuid

INTERNAL_API_KEY = "abc12345"
sessions: dict[str, Session] = dict()
sessions_reverse: dict[int, str] = dict()


def get_token(req: Request):
    try:
        token = req.headers["Authorization"].split(" ")[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    return token


class AuthzContext(BaseModel):
    token: str | None
    roles: list[Role] = [Role.GUEST]


def protect_api(api_key: str):
    if api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED,
            detail='Unauthorized',
        )


def authn(api_key: str, token: str):
    protect_api(api_key)
    global sessions
    if token in sessions:
        try:
            user = get_user_by_id(sessions[token].id)
            if user:
                return AuthContext(id=user.id, role=user.role, organization=user.organization)
        except Exception as e:
            print(e)
    return


def authz(api_key: str, token: str, roles: tuple[str] | None, organiz: tuple[str] | None = None):
    protect_api(api_key)
    global sessions
    if token in sessions:
        try:
            access = False
            user = get_user_by_id(sessions[token].id)
            if user:
                if (roles and user.role in roles) or not roles:
                    access = True
                else:
                    access = False
                if (organiz and user.organization in organiz) or not organiz:
                    access = True
                else:
                    access = False
                if access:
                    return AuthContext(id=user.id, role=user.role, organization=user.organization)
        except Exception as e:
            print(e)
    return


def add_session(user: User):
    if not user:
        return False
    token = str(uuid.uuid4())
    global sessions_reverse
    global sessions
    if user.id in sessions_reverse:
        try:
            sessions.pop(sessions_reverse[user.id])
            sessions_reverse.pop(user.id)
        except Exception as e:
            print(e)
    try:
        sessions[token] = Session(id=user.id, token=token)
        sessions_reverse[user.id] = token
        return token
    except Exception as e:
        print(e)
        return False


def remove_session_by_id(userid: int):
    user = get_user_by_id(userid)
    if not user:
        return False
    global sessions_reverse
    global sessions
    for s in sessions:
        if sessions[s].id == user.id:
            try:
                sessions.pop(s)
            except Exception as e:
                print(e)
    if userid in sessions_reverse:
        try:
            sessions_reverse.pop(user.id)
        except Exception as e:
            print(e)
    return True


def remove_session_by_token(token: str):
    global sessions_reverse
    global sessions
    if token in sessions:
        try:
            id = sessions[token].id
            sessions.pop(token)
            sessions_reverse.pop(id)
            return True
        except Exception as e:
            print(e)
    return False


def check_email_password(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return False
    try:
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user
    except Exception as e:
        print(e)
    return False


def check_used_email_pass(email: str, username: str):
    check = check_email_username_inuse(email=email, username=username)
    if check and (check['email'] or check['username']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email or password is alreay in used"
        )
    # if check and check['email']:
    #     raise HTTPException(
    #     status_code=status.HTTP_400_BAD_REQUEST,
    #     detail="Email is alreay in used"
    # )
    # if check and check['username']:
    #     raise HTTPException(
    #     status_code=status.HTTP_400_BAD_REQUEST,
    #     detail="Username is alreay in used"
    # )


def check_organization(userid: int, organiz: str):
    user = get_user_by_id(userid)
    return user and user.organization == organiz
