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
    interface_type: str
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
    interface_type: str
    name: str | None = None
    host: str | None = None
    username: str | None = None
    password: str | None = None
    from_address: str | None = None
    ignore_cert_errors: bool | None = None
    modified_date: datetime = datetime.now()

    class Config:
        orm_mode = True
