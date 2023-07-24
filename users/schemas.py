from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class Session(BaseModel):
    id: int
    token: str
    create_at: datetime = datetime.now()


class Role(str, Enum):
    GUEST = 'guest'
    PAID = 'paid'
    AUDITOR = 'auditor'
    ADMIN = 'admin'
    SUPER = 'superadmin'


class AuthContext(BaseModel):
    id: int
    role: Role = Role.GUEST
    organization: int = 0


class UserLoginModel(BaseModel):
    email: str = Field(min_length=4, max_length=64)
    password: str = Field(min_length=8, max_length=1024)


class UserModel(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    email: str = Field(min_length=4, max_length=64)
    firstname: str = Field(min_length=1, max_length=64)
    lastname: str = Field(min_length=1, max_length=64)
    phonenumber: str | None = Field(default=None, min_length=1, max_length=16)


class UserCreateModel(UserModel):
    password: str = Field(min_length=8, max_length=1024)


class UserFormModel(UserCreateModel):
    username: str | None = Field(default=None, min_length=1, max_length=32)
    email: str | None = Field(default=None, min_length=4)
    password: str | None = Field(default=None, min_length=1, max_length=1024)
    firstname: str | None = Field(default=None, min_length=1, max_length=64)
    lastname: str | None = Field(default=None, min_length=1, max_length=64)
    phonenumber: str | None = Field(default=None, min_length=1, max_length=16)
    role: Role | None = None
    organization: str | None = Field(
        default=None, min_length=1, max_length=128)
    is_active: bool | None = None


class UserDbModel(UserCreateModel):
    id: int | None
    role: Role = Role.GUEST
    organization: int | None = None
    last_login: datetime | None
    create_at: datetime = datetime.now()
    is_active: bool = True

    class Config:
        orm_mode = True


class UserListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    users: list[UserDbModel] = []
