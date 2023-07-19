from pydantic import BaseModel
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

import sys
# from templates_phishsite.models import Template
# from mailfunc.models import SMTP
# from models import Group, Result

# sys.path.append('/path/to/parent/folder')


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


class TargetModel(BaseModel):
    id: int | None = None
    first_name: str = Field(min_length=1, max_length=128)
    last_name: str = Field(min_length=1, max_length=128)
    email: str = Field(min_length=1, max_length=128)
    position: str = Field(min_length=1, max_length=128)


class TargetFormModel(TargetModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    position: str | None = None


class TargetDisplayModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    position: str | None = None

    class Config:
        orm_mode = True


class GroupDisplayModel(BaseModel):
    id: int | None
    name: str = Field(min_length=1, max_length=128)
    modified_date: datetime | None = datetime.now()
    # visible: VISIBLE = VISIBLE.NONE
    targets: List[TargetDisplayModel] = []

    class Config:
        orm_mode = True


class GroupFormModel(GroupDisplayModel):
    name: str | None = None
    targets: List[TargetFormModel] | None = None


class GroupListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    group: List[GroupDisplayModel] = []

# class TargetModel(BaseModel):
#     email: str = Field(min_length=1, max_length=128)
#     first_name: str = Field(min_length=1, max_length=128)
#     last_name: str = Field(min_length=1, max_length=128)
#     position: str = Field(min_length=1, max_length=128)


# class GroupModel(BaseModel):
#     id: int | None = None
#     user_id: int | None = None
#     name: str = Field(min_length=1, max_length=128)
#     modified_date: datetime = datetime.now()
#     targets: list[TargetModel]


# class GroupDisplayModel(GroupModel):
#     user_id: int | None = None
#     name: str | None = None
#     modified_date: datetime = datetime.now()
#     targets: list[TargetModel]

#     class Config:
#         orm_mode = True


# class GroupListModel(BaseModel):
#     count: int = 0
#     page: int = 1
#     last_page: int = 1
#     limit: int = 25
#     group: list[GroupModel] = []
