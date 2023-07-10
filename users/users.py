import uvicorn
from datetime import datetime
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from schemas import (UserCreateModel, UserFormModel, UserLoginModel,
                     UserDbModel, Role, UserListModel)
from models import (engine, create_user, get_all_users,
                    get_user_by_organize, Base, update_last_login,
                    get_user_by_id, update_user, delete_user)
from auth import (get_token, authn, authz, add_session, remove_session_by_token,
                  check_email_password, check_used_email_pass, check_organization)
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import re
import os


load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    detail = ""
    try:
        detail = exc.errors()[0]['loc'][-1]+','+exc.errors()[0]['msg']
    except Exception as e:
        print(e)
        detail = str(exc.errors())
    return JSONResponse({'detail': detail},
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post('/authn')
def token_authentication(req: Request):
    try:
        api_key = req.body['api_key']
        token = req.body['token']
        result = authn(api_key, token)
        return result
    except:
        raise HTTPException(
            status_code=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED,
            detail='Unauthorized',
        )


@app.post('/authz')
def token_authentication(req: Request):
    try:
        api_key = req.body['api_key']
        token = req.body['token']
        roles = None
        organiz = None
        if 'roles' in req.body:
            roles = tuple(req.body['roles'])
        if 'organization' in req.body:
            organiz = tuple(req.body['organization'])
        result = authz(api_key, token, roles, organiz)
        if result:
            return result
    except:
        raise HTTPException(
            status_code=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED,
            detail='Unauthorized',
        )


@app.post('/register')
def register(u: UserCreateModel):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not (re.fullmatch(regex, u.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid email format"
        )
    check_used_email_pass(email=u.email, username=u.username)
    user = UserDbModel(username=u.username,
                       email=u.email,
                       firstname=u.firstname,
                       lastname=u.lastname,
                       phonenumber=u.phonenumber,
                       password=u.password,
                       role=Role.GUEST,
                       organization='None',
                       create_at=datetime.now(),
                       is_active=True)
    u = create_user(user)
    if u:
        return {
            'username': u.username,
            'email': u.email,
            'firstname': u.firstname,
            'lastname': u.lastname,
            'role': u.role,
            'is_active': u.is_active
        }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot register user. Please try again later"
    )


@app.post('/login')
def login(u: UserLoginModel):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not (re.fullmatch(regex, u.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid email format"
        )
    user = check_email_password(u.email, u.password)
    if user:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="account is not activated"
            )
        token = add_session(user)
        if token:
            update_last_login(user.id)
            return {'username': user.username,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'organization': user.organization,
                    'role': user.role,
                    'token': token}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot login. Please Check Email and Password and try again"
    )


@app.post('/logout')
def logout(token: str = Depends(get_token)):
    if check_login(token) and remove_session_by_token(token):
        return {'success': True}
    return {'success': False}


@app.get('/me')
def about_me(token: str = Depends(get_token)):
    authcontext = check_role(token=token, roles=(
        Role.GUEST, Role.PAID, Role.ADMIN, Role.SUPER, Role.AUDITOR))
    user = get_user_by_id(authcontext.id)
    if user:
        return {'username': user.username,
                'email': user.email,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'phonenumber': user.phonenumber,
                'organization': user.organization,
                'role': user.role,
                'last_login': user.last_login,
                'create_at': user.create_at}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized"
    )


@app.get('/users', response_model=UserListModel)
def get_users(token: str = Depends(get_token), page: int | None = None, limit: int | None = None):
    authcontext = check_role(token=token, roles=(
        Role.ADMIN, Role.SUPER, Role.AUDITOR))
    if page and page < 0:
        page = 1
    if limit and limit < 1:
        limit = 25
    user = None
    if authcontext.role == Role.SUPER:
        user = get_all_users(page, limit)
    elif authcontext.role in (Role.ADMIN, Role.AUDITOR):
        user = get_user_by_organize(authcontext.organization, page, limit)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    if user and 'users' in user:
        return UserListModel(count=user['count'], page=user['page'],
                             last_page=(user['count']//user['limit'])+1,
                             limit=user['limit'],
                             users=user['users'])
    return UserListModel()


@app.get('/users/{userid}', response_model=UserDbModel)
def get_users(userid: int, token: str = Depends(get_token)):
    authcontext = check_role(token=token, roles=(
        Role.ADMIN, Role.SUPER, Role.AUDITOR))
    if authcontext.role == Role.SUPER:
        user = get_user_by_id(userid)
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not Found user of id :{userid}"
        )
    elif authcontext.role in (Role.ADMIN, Role.AUDITOR):
        user = get_user_by_id(userid)
        if user and user.organization == authcontext.organization:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized"
    )


@app.post('/users', response_model=UserDbModel)
def add_user(user: UserDbModel, token: str = Depends(get_token)):
    authcontext = check_role(token=token, roles=(Role.ADMIN, Role.SUPER))
    check_used_email_pass(email=user.email, username=user.username)
    user.id = None
    user.last_login = None
    user.create_at = datetime.now()

    result = None
    if authcontext.role == Role.SUPER:
        result = create_user(user)
    elif authcontext.role == Role.ADMIN:
        user.role = Role.AUDITOR
        user.organization = authcontext.organization
        result = create_user(user)
    if result:
        return result

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized"
    )


@app.put('/users/{userid}', response_model=UserDbModel)
def modify_user(userid: int, user: UserFormModel, token: str = Depends(get_token)):
    authcontext = check_role(token=token, roles=(
        Role.ADMIN, Role.SUPER, Role.AUDITOR, Role.PAID, Role.GUEST))
    temp_user = dict()
    if user.username:
        temp_user['username'] = user.username
    if user.email:
        temp_user['email'] = user.email
    if user.password:
        temp_user['password'] = user.password
    if user.firstname:
        temp_user['firstname'] = user.firstname
    if user.lastname:
        temp_user['lastname'] = user.lastname
    if user.phonenumber:
        temp_user['phonenumber'] = user.phonenumber

    if authcontext.role == Role.SUPER:
        if user.role and userid != authcontext.id:
            temp_user['role'] = user.role
        if user.organization:
            temp_user['organization'] = user.organization
        if user.is_active and userid != authcontext.id:
            temp_user['is_active'] = user.is_active

        check_updata_email_pass(temp_user)
        u = update_user(userid, temp_user)
        if u:
            return u

    elif authcontext.role == Role.ADMIN:
        if user.role and userid != authcontext.id:
            if user.role not in (Role.AUDITOR, Role.ADMIN):
                user.role = Role.AUDITOR
            temp_user['role'] = user.role
        if user.is_active and userid != authcontext.id:
            temp_user['is_active'] = user.is_active
        check_updata_email_pass(temp_user)
        check_organization(userid, authcontext.organization)
        u = update_user(userid, temp_user)
        if u:
            return u
    else:
        if userid != authcontext.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        check_updata_email_pass(temp_user)
        u = update_user(userid, temp_user)
        if u:
            return u

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.delete('/users/{userid}')
def del_user(userid: int, token: str = Depends(get_token)):
    authcontext = check_role(token=token, roles=(Role.ADMIN, Role.SUPER))
    if authcontext.role == Role.SUPER:
        if delete_user(userid):
            return {'success': True}
        return {'success': False}
    elif authcontext.role == Role.ADMIN:
        if userid != authcontext.id and \
                check_organization(userid, authcontext.organization):
            if delete_user(userid):
                return {'success': True}
            return {'success': False}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized"
    )


def check_role(token: str, roles: tuple | None, organiz: tuple | None = None):
    result = authz(api_key='abc12345', token=token,
                   roles=roles, organiz=organiz)
    if result:
        return result
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized"
    )


def check_login(token: str):
    result = authn(api_key='abc12345', token=token)
    if result:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized"
    )


def check_updata_email_pass(temp: dict):
    if 'email' in temp and 'username' in temp:
        check_used_email_pass(temp['email'], temp['username'])
    elif 'email' in temp:
        check_used_email_pass(temp['email'], None)
    elif 'username' in temp:
        check_used_email_pass(None, temp['username'])


if __name__ == "__main__":
    create_user(UserDbModel(username='alongkot',
                            email='along@gmail.com',
                            firstname='alongkot',
                            lastname='chai',
                            phonenumber='0839145961',
                            password='123456789',
                            role=Role.SUPER,
                            organization='None',
                            is_active=True))
    uvicorn.run(app, host=os.getenv('HOST'), port=os.getenv('PORT'))
