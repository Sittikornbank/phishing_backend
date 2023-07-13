from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from schemas import SMTPDisplayModel, SMTPListModel, IMAPListModel, SMTPFormModel, IMAPModel, IMAPDisplayModel
from datetime import datetime
from dotenv import load_dotenv
import bcrypt
import os


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SMTP(Base):
    __tablename__ = "smtp"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    interface_type = Column(String(64))
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


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all_smtp(page: int | None = None, size: int | None = None):
    db: Session = next(get_db())
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
    db: Session = next(get_db())
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


def get_smtp():
    db: Session = next(get_db())
    try:
        return db.query(SMTP).all()
    except Exception as e:
        print(e)
    return


def get_imap():
    db: Session = next(get_db())
    try:
        return db.query(IMAP).all()
    except Exception as e:
        print(e)
    return


def get_smtp_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(SMTP).filter(SMTP.id == id).first()
    except Exception as e:
        print(e)
    return


def get_imap_id(user_id: int):
    db: Session = next(get_db())
    try:
        return db.query(IMAP).filter(IMAP.user_id == user_id).first()
    except Exception as e:
        print(e)
    return


def create_smtp(smtp: SMTPDisplayModel):
    db: Session = next(get_db())
    try:
        send = SMTP(user_id=smtp.user_id,
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


def create_imap(imap: IMAPDisplayModel):
    db: Session = next(get_db())
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


def update_smtp(db: Session, id: int, smtp: dict):
    db: Session = next(get_db())
    try:
        db.query(SMTP).filter(SMTP.id == id).update(smtp)
        db.commit()
        return get_smtp_id(id)
    except Exception as e:
        print(e)
    return


def update_imap(db: Session, user_id: int, imap: dict):
    db: Session = next(get_db())
    try:
        db.query(IMAP).filter(IMAP.user_id == user_id).update(imap)
        db.commit()
        return get_imap_id(user_id)
    except Exception as e:
        print(e)
    return


def delete_smtp(db: Session, id: int):
    db: Session = next(get_db())
    try:
        db.query(SMTP).filter(SMTP.id == id).delete()
        db.commit()
    except Exception as e:
        print(e)
    return


def delete_imap(db: Session, user_id: int):
    db: Session = next(get_db())
    try:
        db.query(IMAP).filter(IMAP.user_id == user_id).delete()
        db.commit()
        return True
    except Exception as e:
        print(e)
    return
