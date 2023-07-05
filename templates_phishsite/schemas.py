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
    organization: str = 'None'


class Visible(str, Enum):
    ALL = 'all'
    PAID = 'paid'
    NONE = 'none'
    CUSTOM = 'custom'


class ParentModel(BaseModel):
    id: int | None = None
    name: str = Field(min_length=1, max_length=128)
    modified_date: datetime = datetime.now()
    create_at: datetime = datetime.now()
    visible: Visible = Visible.NONE
    owner_id: int | None = None
    organize_id: int | None = None


class TemplateModel(ParentModel):
    description: str = ""
    site_template: int | None = None
    mail_template: int | None = None


class SiteModel(ParentModel):
    html: str = ""
    capture_credentials: bool = False
    capture_passwords: bool = False


class EmailModel(ParentModel):
    envelope_sender: str = ""
    subject: str = ""
    html: str = ""
    attachments: str = ""


class SiteFormModel(SiteModel):
    name: str | None = None
    html: str | None = None
    capture_credentials: bool | None = None
    capture_passwords: bool | None = None
    modified_date: datetime | None = None
    create_at: datetime | None = None
    visible: Visible | None = None
    owner_id: int | None = None
    organize_id: int | None = None


class EmailFormModel(EmailModel):
    name: str | None = None
    envelope_sender: str | None = None
    subject: str | None = None
    html: str | None = None
    attachments: str | None = None
    modified_date: datetime | None = None
    create_at: datetime | None = None
    visible: Visible | None = None
    owner_id: int | None = None
    organize_id: int | None = None


class TemplateFromModel(TemplateModel):
    name: str | None = None
    modified_date: datetime | None = None
    create_at: datetime | None = None
    visible: Visible | None = None
    owner_id: int | None = None
    organize_id: int | None = None
    description: str | None = None
    site_template: int | None = None
    mail_template: int | None = None


class SiteDisplayModel(BaseModel):
    id: int | None = None
    name: str | None = None
    html: str | None = None

    class Config:
        orm_mode = True


class EmailDisplayModel(BaseModel):
    id: int | None = None
    name: str | None = None
    envelope_sender: str | None = None
    subject: str | None = None
    html: str | None = None
    attachments: str | None = None

    class Config:
        orm_mode = True


class TemplateDisplayModel(BaseModel):
    id: int | None = None
    name: str = ""
    description: str = ""
    site_template: SiteDisplayModel
    mail_template: EmailDisplayModel
    modified_date: datetime = datetime.now()
    create_at: datetime = datetime.now()
    visible: Visible = Visible.NONE
    owner_id: int | None = None
    organize_id: int | None = None

    class Config:
        orm_mode = True
