from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class Role(str, Enum):
    GUEST = 'guest'
    PAID = 'paid'
    AUDITOR = 'auditor'
    ADMIN = 'admin'
    SUPER = 'superadmin'


class Event(str, Enum):
    OPEN = 'open'
    CLICK = 'click'
    SUBMIT = 'submit'


class AuthContext(BaseModel):
    id: int
    role: Role = Role.GUEST
    organization: int | None = None


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
    org_id: int | None = None


class TemplateModel(ParentModel):
    description: str = ""
    site_template: int | None = None
    mail_template: int | None = None

    class Config:
        orm_mode = True


class SiteModel(ParentModel):
    html: str = ""
    capture_credentials: bool = False
    capture_passwords: bool = False
    redirect_url: str = ""
    phishsite_id: int | None = None
    image_site: str = ""

    class Config:
        orm_mode = True


class EmailModel(ParentModel):
    envelope_sender: str = ""
    subject: str = ""
    html: str = ""
    attachments: list[str] = []
    image_email: str = ""

    class Config:
        orm_mode = True


class SiteFormModel(SiteModel):
    name: str | None = None
    html: str | None = None
    capture_credentials: bool | None = None
    capture_passwords: bool | None = None
    redirect_url: str | None = None
    image_site: str | None = None
    visible: Visible | None = None
    owner_id: int | None = None
    org_id: int | None = None
    phishsite_id: int | None = None


class EmailFormModel(EmailModel):
    name: str | None = None
    envelope_sender: str | None = None
    subject: str | None = None
    html: str | None = None
    attachments: list[str] | None = None
    image_email: str | None = None
    visible: Visible | None = None
    owner_id: int | None = None
    org_id: int | None = None


class TemplateFromModel(TemplateModel):
    name: str | None = None
    visible: Visible | None = None
    owner_id: int | None = None
    org_id: int | None = None
    description: str | None = None
    site_template: int | None = None
    mail_template: int | None = None


class SiteDisplayModel(BaseModel):
    id: int | None = None
    name: str | None = None
    html: str | None = None
    redirect_url: str | None = None
    capture_credentials: bool | None = None
    capture_passwords: bool | None = None
    image_site: str | None = None

    class Config:
        orm_mode = True


class EmailDisplayModel(BaseModel):
    id: int | None = None
    name: str | None = None
    envelope_sender: str | None = None
    subject: str | None = None
    html: str | None = None
    attachments: list[str] | None = None
    image_email: str | None = None

    class Config:
        orm_mode = True


class TemplateDisplayModel(BaseModel):
    id: int | None = None
    name: str = ""
    description: str = ""
    email_templates: EmailDisplayModel | None
    site_templates: SiteDisplayModel | None
    modified_date: datetime | None = datetime.now()
    create_at: datetime | None = datetime.now()
    visible: Visible | None = Visible.NONE
    owner_id: int | None = None
    org_id: int | None = None

    class Config:
        orm_mode = True


class TemplateListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    templates: list[TemplateDisplayModel] = []


class SiteListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    site_templates: list[SiteModel] = []


class EmailListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    email_templates: list[EmailModel] = []


class PhishsiteModel(BaseModel):
    id: int | None = None
    name: str = Field(min_length=1, max_length=128)
    uri: str = Field(min_length=1, max_length=128)
    secret_key: str = Field(max_length=512)

    class Config:
        orm_mode = True


class PhishsiteFromModel(PhishsiteModel):
    id: int | None = None
    name: str | None = None
    uri: str | None = None
    secret_key: str | None = None


class PhishsiteListModel(BaseModel):
    count: int = 0
    page: int = 1
    last_page: int = 1
    limit: int = 25
    phishsites: list[PhishsiteModel] = []


class EventContext(BaseModel):
    ref_key: str
    ref_id: str
    event_type: Event
    payload: str | None


class TemplateReqModel(BaseModel):
    ref_key: str
    ref_ids: list[str]
    template_id: int
    start_at: int


class LaunchingModel(BaseModel):
    req: TemplateReqModel
    auth: AuthContext


class Task(BaseModel):
    ref_key: str
    ref_ids: list[str]
    start_at: int
    site: SiteModel | None = None
    worker_id: int
    org_id: int | None = None
    user_id: int


class EmailResSchema(BaseModel):
    id: int | None = None
    name: str = ""
    envelope_sender: str = ""
    subject: str = ""
    html: str = ""
    attachments: list[str] = []
    base_url: str = ""

    class Config:
        orm_mode = True
