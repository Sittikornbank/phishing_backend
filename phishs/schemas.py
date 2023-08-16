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


class EventType(str, Enum):
    FAIL = 'fail'
    SEND = 'send_email'
    OPEN = 'open_email'
    CLICK = 'click_link'
    SUBMIT = 'submit_data'
    REPORT = 'report'


class AuthContext(BaseModel):
    id: int
    role: Role = Role.GUEST
    organization: int = 0


class CampaignSchema(BaseModel):
    id: int
    user_id: int = 0
    org_id: int = 0
    name: str = ""
    created_date: datetime = datetime.now()
    completed_date: datetime | None
    templates_id: int | None = None
    status: Status = Status.IDLE
    smtp_id: int | None = None
    launch_date: datetime = datetime.now()
    send_by_date: datetime | None = datetime.now()


class EmailSchema(BaseModel):
    id: int | None = None
    name: str = ""
    envelope_sender: str = ""
    subject: str = ""
    html: str = ""
    attachments: list[str] = []
    base_url: str = ""


class SMTPModel(BaseModel):
    id: int | None = None
    interface_type: str = "smtp"
    name: str = Field(min_length=1, max_length=128)
    host: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128)
    from_address: str = Field(min_length=1, max_length=128)
    ignore_cert_errors: bool


class Target(BaseModel):
    id: int
    ref: str | None = None
    email: str
    firstname: str | None = ""
    lastname: str | None = ""
    position: str | None = ""
    phonenumber: str | None = ""
    department: str | None = ""


class EmailReqModel(BaseModel):
    task_id: str
    smtp_id: int = Field(gt=0)
    subject: str = ""
    sender: str = ""
    html: str = ""
    attachments: list[str] = []
    status: Status = Status.IDLE
    duration: int | None = Field(ge=0)
    targets: list[Target] = []
    base_url: str = ""


class TemplateReqModel(BaseModel):
    ref_key: str
    ref_ids: list[str]
    template_id: int
    start_at: int


class BaseReportContext(BaseModel):
    timestamp: int
    ref: str
    event: str
    event_type: str


class SiteStatus(BaseReportContext):
    playload: str


class EmailStatus(BaseReportContext):
    task_id: int


class LaunchModel(BaseModel):
    auth: AuthContext
    campaign: CampaignSchema
    targets: list[Target]


class CampaignManager(BaseModel):
    id: int
    ref: str
    start_date: datetime | None
    end_date: datetime | None
    email_template: EmailSchema | None = None
    smtp: SMTPModel | None = None
    targets: list[Target] = []
    target_index_set: dict[str, tuple[set[EventType], str]]


class CompleteSchema(BaseModel):
    campaign_id: int
    auth: AuthContext


class EventInModel(BaseModel):
    call_from: str
    ref_key: str
    ref_id: str
    event_type: EventType
    details: dict | None = None


class EventOutModel(BaseModel):
    campaign_id: int
    r_id: str
    email: str
    message: EventType
    details: dict | None = None


class EventContext(BaseModel):
    sender: str
    ref_key: str
    ref_id: str
    event_type: EventType
    payload: dict | None = None
