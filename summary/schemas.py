from pydantic import BaseModel
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

import sys


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
    organization: str = 'None'


class AuthContext(BaseModel):
    id: int
    role: Role = Role.GUEST
    organization: int = 0


class Visible(str, Enum):
    ALL = 'all'
    PAID = 'paid'
    NONE = 'none'
    CUSTOM = 'custom'


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

###########################


class CampaignModel(BaseModel):
    id: int | None = None
    user_id: int | None = None
    name: str = Field(min_length=1, max_length=128)
    create_date: datetime = datetime.now()
    complate: datetime = datetime.now()
    templates_id: int | None = None
    status: str = ""
    url: str = ""
    smtp_id: int | None = None
    launch_date: datetime | None = None
    send_by_date: datetime | None = None
    # visible: Visible | None = None
    # owner_id: int | None = None
    # org_id: int | None = None


class CampaignFormModel(CampaignModel):
    user_id: int | None = None
    name: str | None = None
    create_date: datetime | None = None

    templates_id: int | None = None
    status: str | None = None
    url: str | None = None
    smtp_id: int | None = None
    visible: Visible | None = None
    owner_id: int | None = None
    org_id: int | None = None


class CampaignDisplayModel(BaseModel):
    id: int | None = None
    user_id: int | None = None
    name: str | None = None
    create_date: datetime = datetime.now()
    templates_id: int | None = None  # update from templates_phishsite
    status: str | None = None
    url: str | None = None
    smtp_id: int | None = None

    class Config:
        orm_mode = True


class CampaignListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    campaign: list[CampaignDisplayModel] = []
