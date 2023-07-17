from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

import sys
# from templates_phishsite.models import Template
# from mailfunc.models import SMTP
# from models import Group, Result

# sys.path.append('/path/to/parent/folder')


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


class Visible(str, Enum):
    ALL = 'all'
    PAID = 'paid'
    NONE = 'none'
    CUSTOM = 'custom'


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
    launch_date: datetime
    send_by_date: datetime
    visible: Visible | None = None
    owner_id: int | None = None
    org_id: int | None = None


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

# class CampaignStatus(Enum):
#     CampaignQueued = "queued"
#     CampaignInProgress = "in_progress"
#     CampaignComplete = "complete"


# class CampaignModel(BaseModel):

#     id: int | None = None
#     user_id: int | None = None
#     name: str = Field(min_length=1, max_length=128)
#     created_date: datetime = datetime.now()
#     launch_date: datetime
#     send_by_date: datetime
#     completed_date: datetime = datetime.now()
#     template_id: int | None = None
#     template: "Template"
#     status: CampaignStatus
#     results: List["Result"]
#     groups: List["Group"]
#     events: List["Event"]
#     smtp_id: int | None = None
#     smtp: "SMTP"
#     url: str = ""
#     visible: Visible | None = None
#     owner_id: int | None = None
#     org_id: int | None = None


# class CampaignFormModel(CampaignModel):
#     user_id: int | None = None
#     name: str | None = None
#     templates_id: int | None = None
#     template: "Template" | None = None
#     status: CampaignStatus | None = None
#     results: List["Result"] | None = None
#     groups: List["Group"] | None = None
#     events: List["Event"] | None = None
#     smtp_id: int | None = None
#     smtp: "SMTP" | None = None
#     url: str | None = None
#     visible: Visible | None = None
#     owner_id: int | None = None
#     org_id: int | None = None


# class CampaignDisplayModel(BaseModel):
#     id: int | None = None
#     user_id: int | None = None
#     name: str | None = None
#     templates_id: int | None = None
#     template: "Template" | None = None
#     status: CampaignStatus | None = None
#     results: List["Result"] | None = None
#     groups: List["Group"] | None = None
#     events: List["Event"] | None = None
#     smtp_id: int | None = None
#     smtp: "SMTP" | None = None
#     url: str | None = None

#     class Config:
#         orm_mode = True


# class CampaignListModel(BaseModel):
#     count: int = 0
#     page: int = 1
#     last_page: int = 1
#     limit: int = 25
#     campaign: list[CampaignDisplayModel] = []


# class CampaignResults(BaseModel):
#     id: int
#     name: str
#     status: str
#     results: List["Result"]
#     events: List["Event"]


# class CampaignSummaries(BaseModel):
#     total: int
#     campaigns: List["CampaignSummary"]


# class CampaignSummary(BaseModel):
#     id: int
#     created_date: datetime
#     launch_date: datetime
#     send_by_date: datetime
#     completed_date: datetime
#     status: str
#     name: str
#     stats: "CampaignStats"


# class CampaignStats(BaseModel):
#     total: int
#     emails_sent: int
#     opened_email: int
#     clicked_link: int
#     submitted_data: int
#     email_reported: int
#     error: int


# class Event(BaseModel):
#     id: int
#     campaign_id: int
#     email: str
#     time: datetime
#     message: str
#     details: str


# class EventDetails(BaseModel):
#     payload: dict
#     browser: dict


# class EventError(BaseModel):
#     error: str
