from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from db import Base


class PERMIT(Enum):
    SUPER = ['superadmin']
    ORGANIZE = ['audit', 'admin', 'superadmin']
    PAID = ['paid', 'audit', 'admin', 'superadmin']
    ALL = ['guest', 'paid', 'audit', 'admin', 'superadmin']


class VISIBLE(Enum):
    ALL: str = 'all'
    PAID: str = 'paid'
    NONE: str = 'none'


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(256))
    envelope_sender = Column(String(256))
    subject = Column(String(512), default="")
    html = Column(Text, default="")
    attachments = Column(String(512), default="")
    modified_date = Column(String(64))
    visible = Column(String(32), default=VISIBLE.NONE)


class PhishSite(Base):
    __tablename__ = "phishsites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(256))
    html = Column(Text, default="")
    capture_credentials = Column(Boolean, default=False)
    capture_passwords = Column(Boolean, default=False)
    modified_date = Column(String(64))
    visible = Column(String(32), default=VISIBLE.NONE)


class BaseTemplate(BaseModel):
    id: int | None
    name: str
    html: str = ""
    modified_date: datetime = datetime.now()
    visible: VISIBLE = VISIBLE.NONE


class EmailTemplate(BaseTemplate):
    envelope_sender: str
    subject: str = ""
    attachments: list = []

    class Config:
        orm_mode = True


class TemplateUpdate(EmailTemplate):
    name: str | None = None
    html: str | None = None
    envelope_sender: str | None = None
    subject: str | None = None
    attachments: str | None = None
    visible: VISIBLE | None = None


class SiteTemplate(BaseTemplate):
    capture_credentials: bool = False
    capture_passwords: bool = False
    redirect_url: str = ""

    class Config:
        orm_mode = True


class SiteUpdate(SiteTemplate):
    name: str | None = None
    html: str | None = None
    capture_credentials: bool | None = None
    capture_passwords: bool | None = None
    redirect_url: str | None = None
    visible: VISIBLE | None = None


class UserContext(BaseModel):
    uid: int
    role: str
    organization: str | None


def get_ts(db: Session):
    return db.query(Template).all()


def get_t(db: Session, id: int):
    return db.query(Template).filter(Template.id == id).first()


def create_t(db: Session, template: EmailTemplate):
    temp = Template(name=template.name,
                    envelope_sender=template.envelope_sender,
                    subject=template.subject,
                    html=template.html,
                    attachments=str(template.attachments),
                    modified_date=str(template.modified_date),
                    visible=template.visible.value
                    )
    db.add(temp)
    db.commit()
    db.refresh(temp)
    return temp


def update_t(db: Session, id: int, template: dict):
    db.query(Template).filter(Template.id == id).update(template)
    db.commit()
    return get_t(db, id)


def delete_t(db: Session, id: int):
    db.query(Template).filter(Template.id == id).delete()
    db.commit()
