from pydantic import BaseModel
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class Role(str, Enum):
    GUEST = 'guest'
    PAID = 'paid'
    AUDITOR = 'auditor'
    ADMIN = 'admin'
    SUPER = 'superadmin'


class Status(str, Enum):
    IDLE = 'idle'
    RUNING = 'running'
    COMPLETE = 'complete'
    FAIL = 'fail'


class AuthContext(BaseModel):
    id: int
    role: Role = Role.GUEST
    organization: int = 0


class TargetModel(BaseModel):
    id: int | None = None
    firstname: str = Field(max_length=128, default="")
    lastname: str = Field(max_length=128, default="")
    email: str = Field(min_length=1, max_length=128)
    position: str = Field(max_length=128, default="")
    department: str = Field(max_length=128, default="")
    phonenumber: str = Field(max_length=16, default="")

    class Config:
        orm_mode = True


class GroupModel(BaseModel):
    id: int | None
    name: str = Field(min_length=1, max_length=128)
    modified_date: datetime | None = datetime.now()
    user_id: int = Field(gt=0)
    targets: list[TargetModel] = []


class GroupDisplayModel(BaseModel):
    id: int | None
    name: str = ''
    user_id: int | None = None
    modified_date: datetime | None = None
    targets: list[TargetModel] = []

    class Config:
        orm_mode = True


class GroupFormModel(BaseModel):
    name: str | None = None
    targets_to_add: list[TargetModel] | None = None
    targets_to_remove: list[int] | None = None


class BaseListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25

    class Config:
        orm_mode = True


class GroupListModel(BaseListModel):
    groups: List[GroupDisplayModel] = []


class GroupSuperListModel(GroupListModel):
    org_id: int | None = None


class GroupSumModel(BaseModel):
    id: int | None
    name: str | None
    modified_date: datetime | None
    num_targets: int | None


class GroupSumListModel(BaseListModel):
    groups: List[GroupDisplayModel] = []


class GroupSuperSumListModel(GroupSumListModel):
    org_id: int | None = None
###########################


class CampaignModel(BaseModel):
    id: int | None = None
    user_id: int | None = None
    org_id: int | None = None
    name: str = Field(min_length=1, max_length=128)
    create_date: datetime = datetime.now()
    complate: datetime | None = None
    templates_id: int | None = None
    status: Status = Status.IDLE
    smtp_id: int | None = None
    launch_date: datetime = datetime.now()
    send_by_date: datetime | None = None


class CampaignFormModel(CampaignModel):
    user_id: int | None = None
    org_id: int | None = None
    name: str | None = None
    templates_id: int | None = None
    smtp_id: int | None = None
    launch_date: datetime | None = None
    send_by_date: datetime | None = None


class CampaignDisplayModel(BaseModel):
    id: int | None = None
    user_id: int | None = None
    org_id: int | None = None
    name: str | None = None
    create_date: datetime | None = None
    templates_id: int | None = None
    status: str | None = None
    smtp_id: int | None = None
    complate: datetime | None = None
    launch_date: datetime | None = None
    send_by_date: datetime | None = None

    class Config:
        orm_mode = True


class CampaignListModel(BaseListModel):
    campaign: list[CampaignDisplayModel] = []
