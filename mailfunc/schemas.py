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
    STOP = 'stop'


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
    organization: int | None = None


class Session(BaseModel):
    id: int
    token: str
    create_at: datetime = datetime.now()


class SMTPModel(BaseModel):
    id: int | None = None
    user_id: int | None = None
    org_id: int | None = None
    interface_type: str = "smtp"
    name: str = Field(min_length=1, max_length=128)
    host: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=128)
    from_address: str = Field(min_length=1, max_length=128)
    ignore_cert_errors: bool
    # headers: str
    modified_date: datetime = datetime.now()


class SMTPFormModel(SMTPModel):
    user_id: int | None = None
    org_id: int | None = None
    interface_type: str | None = None
    name: str | None = None
    host: str | None = None
    username: str | None = None
    password: str | None = None
    from_address: str | None = None
    ignore_cert_errors: bool | None = None
    # headers: str | None = None


class SMTPDisplayModel(BaseModel):
    id: int | None = None
    user_id: int | None = None
    org_id: int | None
    interface_type: str | None = None
    name: str | None = None
    host: str | None = None
    username: str | None = None
    from_address: str | None = None
    ignore_cert_errors: bool | None = None
    modified_date: datetime = datetime.now()

    class Config:
        orm_mode = True


class SMTPListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    smtp: list[SMTPDisplayModel] = []

    class Config:
        orm_mode = True


class IMAPModel(BaseModel):
    user_id: int | None = None
    org_id: int | None = None
    enabled: bool | None = None
    host: str = Field(min_length=1, max_length=128)
    port: int | None = None
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=128)
    tls: bool | None = None
    ignore_cert_errors: bool | None = None
    folder: str = Field(min_length=1, max_length=128)
    restrict_domain: str = Field(min_length=1, max_length=128)
    delete_reported_campaign_email: bool | None = None
    last_login: datetime
    modified_date: datetime = datetime.now()
    imap_freq: int | None = None


class IMAPFormModel(IMAPModel):
    enabled: bool | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    tls: bool | None = None
    ignore_cert_errors: bool | None = None
    folder: str | None = None
    restrict_domain: str | None = None
    delete_reported_campaign_email: bool | None = None
    imap_freq: int | None = None


class IMAPDisplayModel(IMAPModel):
    enabled: bool | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None
    tls: bool | None = None
    ignore_cert_errors: bool | None = None
    folder: str | None = None
    restrict_domain: str | None = None
    delete_reported_campaign_email: bool | None = None
    last_login: datetime | None = None
    modified_date: datetime | None = None
    imap_freq: int | None = None

    class Config:
        orm_mode = True


class IMAPListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    imap: list[IMAPDisplayModel] = []

    class Config:
        orm_mode = True


class Target(BaseModel):
    ref: str
    email: str
    firstname: str | None = ''
    lastname: str | None = ''
    position: str | None = ''
    department: str | None = ''
    phonenumber: str | None = ''


class TaskModel(BaseModel):
    task_id: str
    smtp_id: int = Field(gt=0)
    subject: str = ""
    sender: str = ""
    html: str = ""
    attachments: list[str] = []
    status: Status = Status.IDLE
    sent: int = 0
    fail: int = 0
    duration: int = Field(ge=0)
    targets: list[Target] = []
    auth: AuthContext
    base_url: str


class TaskStatModel(BaseModel):
    ref_key: str
    status: Status = Status.IDLE
    total: int = 0
    sent: int = 0
    fail: int = 0
    user_id: int | None = None
    org_id: int | None = None
