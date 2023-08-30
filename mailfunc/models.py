from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from schemas import SMTPModel, SMTPListModel, IMAPListModel, IMAPModel, IMAPDisplayModel, Status
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URL, echo=False,
                       pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SMTP(Base):
    __tablename__ = "smtp"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    org_id = Column(Integer)
    interface_type = Column(String(64), default='smtp')
    name = Column(String(64))
    host = Column(String(64))
    username = Column(String(64), nullable=False)
    password = Column(String(2048), nullable=False)
    from_address = Column(String(256))
    ignore_cert_errors = Column(Boolean, default=True)
    modified_date = Column(DateTime(), default=datetime.now())


class IMAP(Base):
    __tablename__ = "imap"

    user_id = Column(Integer, primary_key=True)
    org_id = Column(Integer)
    enabled = Column(Boolean, default=True)
    host = Column(String(64), nullable=False)
    port = Column(Integer)
    username = Column(String(64), nullable=False)
    password = Column(String(2048), nullable=False)
    tls = Column(Boolean, default=True)
    ignore_cert_errors = Column(Boolean, default=True)
    folder = Column(String(128))
    restrict_domain = Column(String(128))
    delete_reported_campaign_email = Column(Boolean, default=True)
    last_login = Column(DateTime)
    modified_date = Column(DateTime(), default=datetime.now())
    imap_freq = Column(Integer)


def get_all_smtp(page: int | None = None, size: int | None = None):
    with SessionLocal() as db:
        try:
            if not size or size < 0:
                size = 25
            if not page or page < 0:
                page = 1
            smtps = db.query(SMTP).limit(size).offset(size*(page-1)).all()
            count = db.query(SMTP).count()

            return SMTPListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 smtp=smtps)
        except Exception as e:
            print(e)
        return SMTPListModel()


def get_all_imap(page: int | None = None, size: int | None = None):
    with SessionLocal() as db:
        try:
            if not size or size < 0:
                size = 25
            if not page or page < 0:
                page = 1
            imaps = db.query(IMAP).limit(size).offset(size*(page-1)).all()
            count = db.query(IMAP).count()

            return IMAPListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 imap=imaps)
        except Exception as e:
            print(e)
        return IMAPListModel()


def get_smtp_id(id: int):
    with SessionLocal() as db:
        try:
            return db.query(SMTP).filter(SMTP.id == id).first()
        except Exception as e:
            print(e)
        return


def get_imap_id(user_id: int):
    with SessionLocal() as db:
        try:
            return db.query(IMAP).filter(IMAP.user_id == user_id).first()
        except Exception as e:
            print(e)
        return


def get_smtps_by_user(id: int, page: int | None = None, size: int | None = None, include_none: bool = False):
    with SessionLocal() as db:
        try:
            if not size or size < 0:
                size = 25
            if not page or page < 0:
                page = 1
            if include_none:
                smtps = db.query(SMTP).filter(
                    SMTP.user_id == id or SMTP.user_id == None).limit(size).offset(size*(page-1)).all()
                count = db.query(SMTP).filter(
                    SMTP.user_id == id or SMTP.user_id == None).count()
            smtps = db.query(SMTP).filter(
                SMTP.user_id == id).limit(size).offset(size*(page-1)).all()
            count = db.query(SMTP).filter(
                SMTP.user_id == id).count()

            return SMTPListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 smtp=smtps)
        except Exception as e:
            print(e)
        return SMTPListModel()


def get_smtps_by_org(id: int, page: int | None = None, size: int | None = None, include_none: bool = False):
    with SessionLocal() as db:
        try:
            if not size or size < 0:
                size = 25
            if not page or page < 0:
                page = 1
            if include_none:
                smtps = db.query(SMTP).filter(
                    SMTP.org_id == id or SMTP.org_id == None).limit(size).offset(size*(page-1)).all()
                count = db.query(SMTP).filter(
                    SMTP.org_id == id or SMTP.org_id == None).count()
            smtps = db.query(SMTP).filter(
                SMTP.org_id == id).limit(size).offset(size*(page-1)).all()
            count = db.query(SMTP).filter(
                SMTP.org_id == id).count()

            return SMTPListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 smtp=smtps)
        except Exception as e:
            print(e)
        return SMTPListModel()


def get_imap_by_user(id: int, page: int | None = None, size: int | None = None, include_none: bool = False):
    with SessionLocal() as db:
        try:
            if not size or size < 0:
                size = 25
            if not page or page < 0:
                page = 1
            if include_none:
                imaps = db.query(IMAP).filter(
                    IMAP.user_id == id or IMAP.user_id == None).limit(size).offset(size*(page-1)).all()
                count = db.query(IMAP).filter(
                    IMAP.user_id == id or IMAP.user_id == None).count()
            imaps = db.query(IMAP).filter(
                IMAP.user_id == id).limit(size).offset(size*(page-1)).all()
            count = db.query(IMAP).filter(
                IMAP.user_id == id).count()

            return IMAPListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 imap=imaps)
        except Exception as e:
            print(e)
        return IMAPListModel()


def count_smtp_by_user(user_id: int):
    with SessionLocal() as db:
        try:
            return db.query(SMTP).filter(SMTP.user_id == user_id).count()
        except Exception as e:
            print(e)
        return 0


def create_smtp(smtp: SMTPModel):
    with SessionLocal() as db:
        try:
            send = SMTP(user_id=smtp.user_id,
                        org_id=smtp.org_id,
                        interface_type=smtp.interface_type,
                        name=smtp.name,
                        host=smtp.host,
                        username=smtp.username,
                        password=smtp.password,
                        from_address=smtp.from_address,
                        ignore_cert_errors=smtp.ignore_cert_errors,
                        modified_date=smtp.modified_date)
            db.add(send)
            db.commit()
            db.refresh(send)
            return send
        except Exception as e:
            print(e)
        return


def count_imap_by_user(user_id: int):
    with SessionLocal() as db:
        try:
            return db.query(IMAP).filter(IMAP.user_id == user_id).count()
        except Exception as e:
            print(e)
        return 0


def create_imap(imap: IMAPDisplayModel):
    with SessionLocal() as db:
        try:
            read = IMAP(user_id=imap.user_id,
                        enabled=imap.enabled,
                        host=imap.host,
                        port=imap.port,
                        username=imap.username,
                        password=imap.password,
                        tls=imap.tls,
                        ignore_cert_errors=imap.ignore_cert_errors,
                        folder=imap.folder,
                        restrict_domain=imap.restrict_domain,
                        delete_reported_campaign_email=imap.delete_reported_campaign_email,
                        last_login=imap.last_login,
                        imap_freq=imap.imap_freq,
                        modified_date=imap.modified_date)
            db.add(read)
            db.commit()
            db.refresh(read)
            return read
        except Exception as e:
            print(e)
        return


def update_smtp(id: int, smtp: dict):
    with SessionLocal() as db:
        try:
            db.query(SMTP).filter(SMTP.id == id).update(smtp)
            db.commit()
            return get_smtp_id(id)
        except Exception as e:
            print(e)
        return


def update_imap(user_id: int, imap: dict):
    with SessionLocal() as db:
        try:
            db.query(IMAP).filter(IMAP.user_id == user_id).update(imap)
            db.commit()
            return get_imap_id(user_id)
        except Exception as e:
            print(e)
        return


def delete_smtp(id: int):
    with SessionLocal() as db:
        try:
            c = db.query(SMTP).filter(SMTP.id == id).delete()
            db.commit()
            return c > 0
        except Exception as e:
            print(e)
        return


def delete_imap(user_id: int):
    with SessionLocal() as db:
        try:
            c = db.query(IMAP).filter(IMAP.user_id == user_id).delete()
            db.commit()
            return c > 0
        except Exception as e:
            print(e)
        return
