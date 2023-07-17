from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class Role(str, Enum):
    GUEST = 'guest'
    PAID = 'paid'
    AUDITOR = 'auditor'
    ADMIN = 'admin'
    SUPER = 'superadmin'


class Status(str, Enum):
    IDLE = 'idle'
    RUNNING = 'running'
    COMPLETE = 'complete'
    FAIL = 'fail'


class AuthContext(BaseModel):
    id: int
    role: Role = Role.GUEST
    organization: int = 0


class CampaignSchema(BaseModel):
    id: int | None = None
    user_id: int = 0
    org_id: int = 0
    name: str = ""
    create_date: datetime = datetime.now()
    complate: datetime = datetime.now()
    templates_id: int | None = None
    status: Status = Status.IDLE
    url: str = ""
    smtp_id: int | None = None
    launch_date: datetime | None = None
    send_by_date: datetime | None = None


class EmailSchema(BaseModel):
    id: int | None = None
    name: str = ""
    envelope_sender: str = ""
    subject: str = ""
    html: str = ""
    attachments: str = ""


class SMTPModel(BaseModel):
    id: int | None = None
    interface_type: str = "smtp"
    name: str = Field(min_length=1, max_length=128)
    host: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128)
    from_address: str = Field(min_length=1, max_length=128)
    ignore_cert_errors: bool


class Target(BaseModel):
    ref: str
    firstname: str = ''
    lastname: str = ''
    position: str = ''
    phonenumber: str = ''
    email: str


class TaskModel(BaseModel):
    task_id: int = Field(gt=0)
    smtp_id: int = Field(gt=0)
    subject: str = ""
    sender: str = ""
    html: str = ""
    attachments: list[str] = []
    status: Status = Status.IDLE
    sent: int = 0
    duration: int = Field(gt=0)
    targets: list[Target] = []


class BaseReportContext(BaseModel):
    timestamp: int
    ref: str
    event: str
    event_type: str


class SiteStatus(BaseReportContext):
    playload: str


class EmailStatus(BaseReportContext):
    task_id: int
