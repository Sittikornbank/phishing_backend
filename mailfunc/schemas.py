from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class Session(BaseModel):
    id: int
    token: str
    create_at: datetime = datetime.now()


class SMTPModel(BaseModel):
    id: int | None = None
    user_id: int | None = None
    interface_type: str = Field(min_length=1, max_length=128)
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
    # user_id = Column(Integer, primary_key=True)
    # enabled = Column(Boolean, default=True)
    # host = Column(String(64))
    # port = Column(Integer)
    # username = Column(String(64), nullable=False)
    # password = Column(String(2048), nullable=False)
    # tls = Column(Boolean, default=True)
    # ignore_cert_errors = Column(Boolean, default=True)
    # folder = Column(String(128))
    # restrict_domain = Column(String(128))
    # delete_reported_campaign_email = Column(Boolean, default=True)
    # last_login = Column(DateTime)
    # modified_date = Column(DateTime(), default=datetime.now())
    # imap_freq = Column(Integer)


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
