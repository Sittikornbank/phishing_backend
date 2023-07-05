from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from schemas import Visible
from datetime import datetime


DATABASE_URL = "mysql+pymysql://root@127.0.0.1/api?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SiteTemplate(Base):
    __tablename__ = "site_templates"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, unique=True)
    name = Column(String(256), nullable=False)
    html = Column(Text, default="")
    capture_credentials = Column(Boolean, default=False)
    capture_passwords = Column(Boolean, default=False)
    modified_date = Column(String(64))
    create_at = Column(String(64), default=str(datetime.now()))
    visible = Column(String(32), default=Visible.NONE)
    owner_id = Column(Integer, default=None)
    organize_id = Column(Integer, default=None)


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    envelope_sender = Column(String(256), default="")
    subject = Column(String(512), default="")
    html = Column(Text, default="")
    attachments = Column(String(512), default="")
    modified_date = Column(String(64))
    create_at = Column(String(64), default=str(datetime.now()))
    visible = Column(String(32), default=Visible.NONE)
    owner_id = Column(Integer, default=None)
    organize_id = Column(Integer, default=None)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all_email_templates():
    db: Session = next(get_db())
    try:
        return db.query(EmailTemplate).all()
    except Exception as e:
        print(e)
    return


def get_all_site_templates():
    db: Session = next(get_db())
    try:
        return db.query(SiteTemplate).all()
    except Exception as e:
        print(e)
    return


def get_email_template_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(EmailTemplate).filter(EmailTemplate.id == id).first()
    except Exception as e:
        print(e)
    return


def get_site_template_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(SiteTemplate).filter(SiteTemplate.id == id).first()
    except Exception as e:
        print(e)
    return


def get_email_template_by_owner(owner: int):
    db: Session = next(get_db())
    try:
        return db.query(EmailTemplate).filter(EmailTemplate.owner_id == owner).all()
    except Exception as e:
        print(e)
    return


def get_site_template_by_owner(owner: int):
    db: Session = next(get_db())
    try:
        return db.query(SiteTemplate).filter(SiteTemplate.owner_id == owner).all()
    except Exception as e:
        print(e)
    return


# def create_user(user_in: UserDbModel):
#     db: Session = next(get_db())
#     try:
#         user = User(username=user_in.username,
#                     email=user_in.email,
#                     firstname=user_in.firstname,
#                     lastname=user_in.lastname,
#                     password=user_in.password,
#                     role=user_in.role.value,
#                     organization=user_in.organization,
#                     phonenumber=user_in.phonenumber)
#         user.password = (bcrypt.hashpw(user.password.encode(
#             'utf-8'), bcrypt.gensalt())).decode('utf-8')
#         db.add(user)
#         db.commit()
#         db.refresh(user)
#         return user
#     except Exception as e:
#         print(e)
#     return


# def get_user_by_email(email: str):
#     db: Session = next(get_db())
#     try:
#         return db.query(User).filter(User.email == email).first()
#     except Exception as e:
#         print(e)
#     return


# def update_user(id: int, user_in: dict):
#     db: Session = next(get_db())
#     try:
#         if 'password' in user_in:
#             user_in['password'] = (bcrypt.hashpw(user_in['password'].encode(
#                 'utf-8'), bcrypt.gensalt())).decode('utf-8')
#         db.query(User).filter(User.id == id).update(user_in)
#         db.commit()
#         return get_user_by_id(id)
#     except Exception as e:
#         print(e)
#     return


# def update_last_login(id: int):
#     db: Session = next(get_db())
#     try:
#         db.query(User).filter(User.id == id).update(
#             {'last_login': str(datetime.now())})
#         db.commit()
#         return True
#     except Exception as e:
#         print(e)
#     return


# def delete_user(id: int):
#     db: Session = next(get_db())
#     try:
#         db.query(User).filter(User.id == id).delete()
#         db.commit()
#         return True
#     except Exception as e:
#         print(e)
#     return
