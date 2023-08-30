from sqlalchemy import (Column, Integer, String, Boolean,
                        Text, create_engine, ForeignKey, DateTime,
                        JSON)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from schemas import (Visible, EmailModel, SiteModel,
                     TemplateModel, TemplateListModel,
                     SiteListModel, EmailListModel,
                     PhishsiteListModel, PhishsiteModel)
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URI")

engine = create_engine(DATABASE_URL, echo=False,
                       pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Phishsite(Base):
    __tablename__ = "phishsites"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, unique=True)
    name = Column(String(256), nullable=False)
    uri = Column(Text, nullable=False)
    secret_key = Column(String(512))


class SiteTemplate(Base):
    __tablename__ = "site_templates"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, unique=True)
    name = Column(String(256), nullable=False)
    html = Column(Text, default="")
    capture_credentials = Column(Boolean, default=False)
    capture_passwords = Column(Boolean, default=False)
    redirect_url = Column(Text, default="")
    image_site = Column(String(128), default="")
    modified_date = Column(DateTime())
    create_at = Column(DateTime())
    visible = Column(String(32), default=Visible.NONE)
    owner_id = Column(Integer, default=None)
    org_id = Column(Integer, default=None)
    phishsite_id = Column(Integer,
                          ForeignKey('phishsites.id', ondelete='SET NULL',))


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    envelope_sender = Column(String(256), default="")
    subject = Column(String(512), default="")
    html = Column(Text, default="")
    attachments = Column(JSON(), default=[])
    image_email = Column(String(128), default="")
    modified_date = Column(DateTime())
    create_at = Column(DateTime())
    visible = Column(String(32), default=Visible.NONE)
    owner_id = Column(Integer, default=None)
    org_id = Column(Integer, default=None)


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, unique=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, default="")
    site_template = Column(Integer,
                           ForeignKey('site_templates.id',
                                      ondelete='SET NULL',))
    mail_template = Column(Integer,
                           ForeignKey('email_templates.id',
                                      ondelete='SET NULL',))
    modified_date = Column(DateTime())
    create_at = Column(DateTime())
    visible = Column(String(32), default=Visible.NONE)
    owner_id = Column(Integer, default=None)
    org_id = Column(Integer, default=None)


def get_all_email_templates(page: int | None = None, size: int | None = None):
    with SessionLocal() as db:
        try:
            if not size or size < 0:
                size = 25
            if not page or page < 0:
                page = 1
            temps = db.query(EmailTemplate).limit(
                size).offset(size*(page-1)).all()
            count = db.query(EmailTemplate).count()
            return EmailListModel(count=count,
                                  page=page,
                                  limit=size,
                                  last_page=(count//size)+1,
                                  email_templates=temps)
        except Exception as e:
            print(e)
        return EmailListModel()


def get_all_site_templates(page: int | None = None, size: int | None = None):
    with SessionLocal() as db:
        try:
            if not size or size < 0:
                size = 25
            if not page or page < 0:
                page = 1
            temps = db.query(SiteTemplate).offset(size*(page-1)).all()
            count = db.query(SiteTemplate).count()
            return SiteListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 site_templates=temps)
        except Exception as e:
            print(e)
        return SiteListModel()


def get_email_template_by_id(id: int):
    with SessionLocal() as db:
        try:
            return db.query(EmailTemplate).filter(EmailTemplate.id == id).first()
        except Exception as e:
            print(e)
        return


def get_site_template_by_id(id: int):
    with SessionLocal() as db:
        try:
            return db.query(SiteTemplate).filter(SiteTemplate.id == id).first()
        except Exception as e:
            print(e)
        return


def create_email_template(temp: EmailModel):
    with SessionLocal() as db:
        try:
            temp = EmailTemplate(
                name=temp.name,
                html=temp.html,
                envelope_sender=temp.envelope_sender,
                subject=temp.subject,
                attachments=temp.attachments,
                image_email=temp.image_email,
                modified_date=temp.create_at,
                create_at=temp.create_at,
                visible=temp.visible,
                owner_id=temp.owner_id,
                org_id=temp.org_id
            )
            db.add(temp)
            db.commit()
            db.refresh(temp)
            return temp
        except Exception as e:
            print(e)
        return


def create_site_template(temp: SiteModel):
    with SessionLocal() as db:
        try:
            temp = SiteTemplate(
                name=temp.name,
                html=temp.html,
                capture_credentials=temp.capture_credentials,
                capture_passwords=temp.capture_passwords,
                redirect_url=temp.redirect_url,
                image_site=temp.image_site,
                modified_date=temp.create_at,
                create_at=temp.create_at,
                visible=temp.visible,
                owner_id=temp.owner_id,
                org_id=temp.org_id,
                phishsite_id=temp.phishsite_id
            )
            db.add(temp)
            db.commit()
            db.refresh(temp)
            return temp
        except Exception as e:
            print(e)
        return


def update_email_temp(id: int, temp_in: dict):
    with SessionLocal() as db:
        try:
            if temp_in:
                temp_in['modified_date'] = datetime.now()
                db.query(EmailTemplate).filter(
                    EmailTemplate.id == id).update(temp_in)
                db.commit()
                return get_email_template_by_id(id)
        except Exception as e:
            print(e)
        return


def update_site_temp(id: int, temp_in: dict):
    with SessionLocal() as db:
        try:
            if temp_in:
                temp_in['modified_date'] = datetime.now()
                db.query(SiteTemplate).filter(
                    SiteTemplate.id == id).update(temp_in)
                db.commit()
                return get_site_template_by_id(id)
        except Exception as e:
            print(e)
        return


def delete_email_temp(id: int):
    with SessionLocal() as db:
        try:
            c = db.query(EmailTemplate).filter(EmailTemplate.id == id).delete()
            db.commit()
            return c > 0
        except Exception as e:
            print(e)
        return


def delete_site_temp(id: int):
    with SessionLocal() as db:
        try:
            c = db.query(SiteTemplate).filter(SiteTemplate.id == id).delete()
            db.commit()
            return c > 0
        except Exception as e:
            print(e)
        return


def get_all_templates(page: int | None = None, size: int | None = None, show_none: bool = False):
    with SessionLocal() as db:
        try:
            if not size or size < 0:
                size = 25
            if not page or page < 0:
                page = 1
            temps = list()
            count = 0
            temp_db = None
            if show_none:
                count = db.query(Template).count()
                temp_db = db.query(Template, EmailTemplate, SiteTemplate).filter(
                    Template.mail_template == EmailTemplate.id,
                    Template.site_template == SiteTemplate.id).limit(size).offset(size*(page-1))
            else:
                count = db.query(Template).filter(
                    Template.visible != Visible.NONE).count()
                temp_db = db.query(Template, EmailTemplate, SiteTemplate).filter(
                    Template.visible != Visible.NONE,
                    Template.mail_template == EmailTemplate.id,
                    Template.site_template == SiteTemplate.id).limit(size).offset(size*(page-1))
            for tem, etem, stem in temp_db:
                setattr(tem, 'email_templates', etem)
                setattr(tem, 'site_templates', stem)
                temps.append(tem)
            return TemplateListModel(count=count, page=page,
                                     last_page=(count//size)+1,
                                     limit=size,
                                     templates=temps)
        except Exception as e:
            print(e)
            return TemplateListModel()


def get_template_by_id(id: int):
    with SessionLocal() as db:
        try:
            temp, etemp, stemp = db.query(Template, EmailTemplate, SiteTemplate).filter(
                Template.id == id,
                Template.mail_template == EmailTemplate.id,
                Template.site_template == SiteTemplate.id).first()
            setattr(temp, 'email_templates', etemp)
            setattr(temp, 'site_templates', stemp)
            return temp
        except Exception as e:
            print(e)
        return


def create_template(temp_in: TemplateModel):
    with SessionLocal() as db:
        try:
            temp = Template(
                name=temp_in.name,
                description=temp_in.description,
                site_template=temp_in.site_template,
                mail_template=temp_in.mail_template,
                modified_date=temp_in.create_at,
                create_at=temp_in.create_at,
                visible=temp_in.visible,
                owner_id=temp_in.owner_id,
                org_id=temp_in.org_id
            )
            db.add(temp)
            db.commit()
            db.refresh(temp)
            return temp
        except Exception as e:
            print(e)
        return


def update_template(temp_in: dict, id: int):
    with SessionLocal() as db:
        try:
            if temp_in:
                temp_in['modified_date'] = datetime.now()
                db.query(Template).filter(Template.id == id).update(temp_in)
                db.commit()
                return get_template_by_id(id)
        except Exception as e:
            print(e)
        return


def delete_template(id: int):
    with SessionLocal() as db:
        try:
            c = db.query(Template).filter(Template.id == id).delete()
            db.commit()
            return c > 0
        except Exception as e:
            print(e)
        return


def get_all_phishsites(page: int | None = None, size: int | None = None):
    with SessionLocal() as db:
        try:
            if not size or size < 0:
                size = 25
            if not page or page < 0:
                page = 1
            temps = db.query(Phishsite).limit(size).offset(size*(page-1)).all()
            count = db.query(Phishsite).count()

            return PhishsiteListModel(count=count, page=page,
                                      last_page=(count//size)+1,
                                      limit=size,
                                      phishsites=temps)
        except Exception as e:
            print(e)
            return PhishsiteListModel()


def get_phishsite_by_id(id: int):
    with SessionLocal() as db:
        try:
            return db.query(Phishsite).filter(Phishsite.id == id).first()
        except Exception as e:
            print(e)
        return


def create_phishsite(temp_in: PhishsiteModel):
    with SessionLocal() as db:
        try:
            temp = Phishsite(
                name=temp_in.name,
                uri=temp_in.uri,
                secret_key=temp_in.secret_key
            )
            db.add(temp)
            db.commit()
            db.refresh(temp)
            return temp
        except Exception as e:
            print(e)
        return


def update_phishsite(temp_in: dict, id: int):
    with SessionLocal() as db:
        try:
            if temp_in:
                # temp_in['modified_date'] = datetime.now()
                db.query(Phishsite).filter(Phishsite.id == id).update(temp_in)
                db.commit()
                return get_phishsite_by_id(id)
        except Exception as e:
            print(e)
        return


def delete_phishsite(id: int):
    with SessionLocal() as db:
        try:
            c = db.query(Phishsite).filter(Phishsite.id == id).delete()
            db.commit()
            return c > 0
        except Exception as e:
            print(e)
        return
