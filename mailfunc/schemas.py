from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


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


class Session(BaseModel):
    id: int
    token: str
    create_at: datetime = datetime.now()


class SMTPModel(BaseModel):
    id: int | None = None
    user_id: int | None = None
    interface_type: str = "smtp"
    name: str = Field(min_length=1, max_length=128)
    host: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=128)
    from_address: str = Field(min_length=1, max_length=128)
    ignore_cert_errors: bool | None = None
    # headers: str
    modified_date: datetime = datetime.now()


class SMTPFormModel(SMTPModel):
    user_id: int | None = None
    interface_type: str | None = None
    name: str | None = None
    host: str | None = None
    username: str | None = None
    password: str | None = None
    from_address: str | None = None
    ignore_cert_errors: bool | None = None
    # headers: str | None = None
    modified_date: datetime | None = None


class SMTPDisplayModel(SMTPModel):
    id: int | None = None
    user_id: int | None = None
    interface_type: str | None = None
    name: str | None = None
    host: str | None = None
    username: str | None = None
    password: str | None = None
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


class IMAPModel(BaseModel):

    user_id: int | None = None
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
    last_login: datetime | None = None
    modified_date: datetime | None = None
    imap_freq: int | None = None


class IMAPDisplayModel(IMAPModel):
    user_id: int | None = None
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
    last_login: datetime | None = None
    modified_date: datetime = datetime.now()
    imap_freq: int | None = None

    class Config:
        orm_mode = True


class IMAPListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    imap: list[IMAPDisplayModel] = []
