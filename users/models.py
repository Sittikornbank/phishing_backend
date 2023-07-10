from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from schemas import UserDbModel
from datetime import datetime
from dotenv import load_dotenv
import bcrypt
import os


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(64), unique=True, nullable=False)
    password = Column(String(2048), nullable=False)
    firstname = Column(String(64), nullable=False)
    lastname = Column(String(64), nullable=False)
    phonenumber = Column(String(64))
    role = Column(String(64), default='guest', nullable=False)
    organization = Column(String(256))
    last_login = Column(DateTime())
    create_at = Column(DateTime(), default=datetime.now())
    is_active = Column(Boolean, default=False)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all_users(page: int | None = None, size: int | None = None):
    db: Session = next(get_db())
    try:
        if not page and not size:
            users = db.query(User).all()
            return {'users': users, 'count': len(users), 'page': 1, 'limit': len(users)}

        if page and not size:
            size = 25
        elif not page and size:
            page = 1
        if page < 0:
            page = 1
        if size < 0:
            size = 25
        count = db.query(User).count()
        users = db.query(User).limit(size).offset(size*(page-1)).all()
        return {'users': users, 'count': count, 'page': page, 'limit': size}

    except Exception as e:
        print(e)
    return


def get_user_by_organize(organiz: str, page: int | None = None, size: int | None = None):
    db: Session = next(get_db())
    if organiz == 'None':
        return
    try:
        if not page and not size:
            users = db.query(User).filter(User.organization == organiz).all()
            return {'users': users, 'count': len(users), 'page': 1, 'limit': len(users)}

        if page and not size:
            size = 25
        elif not page and size:
            page = 1
        if page < 0:
            page = 1
        if size < 0:
            size = 25
        count = db.query(User).filter(User.organization == organiz).count()
        users = db.query(User).filter(User.organization == organiz).limit(
            size).offset(size*(page-1)).all()
        return {'users': users, 'count': count, 'page': page, 'limit': size}

    except Exception as e:
        print(e)
    return


def get_user_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(User).filter(User.id == id).first()
    except Exception as e:
        print(e)
    return


def check_email_username_inuse(email: str, username: str):
    db: Session = next(get_db())
    result = {'email': False, 'username': False}
    try:
        if email:
            temp = db.query(User).filter(User.email == email).first()
            if temp:
                result['email'] = True
        if username:
            temp = db.query(User).filter(User.username == username).first()
            if temp:
                result['username'] = True
        return result
    except Exception as e:
        print(e)
    return


def create_user(user_in: UserDbModel):
    db: Session = next(get_db())
    try:
        user = User(username=user_in.username,
                    email=user_in.email,
                    firstname=user_in.firstname,
                    lastname=user_in.lastname,
                    password=user_in.password,
                    role=user_in.role.value,
                    organization=user_in.organization,
                    phonenumber=user_in.phonenumber,
                    create_at=user_in.create_at,
                    is_active=user_in.is_active)
        user.password = (bcrypt.hashpw(user.password.encode(
            'utf-8'), bcrypt.gensalt())).decode('utf-8')
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        print(e)
    return


def get_user_by_email(email: str):
    db: Session = next(get_db())
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        print(e)
    return


def update_user(id: int, user_in: dict):
    db: Session = next(get_db())
    try:
        if 'password' in user_in:
            user_in['password'] = (bcrypt.hashpw(user_in['password'].encode(
                'utf-8'), bcrypt.gensalt())).decode('utf-8')
        db.query(User).filter(User.id == id).update(user_in)
        db.commit()
        return get_user_by_id(id)
    except Exception as e:
        print(e)
    return


def update_last_login(id: int):
    db: Session = next(get_db())
    try:
        db.query(User).filter(User.id == id).update(
            {'last_login': datetime.now()})
        db.commit()
        return True
    except Exception as e:
        print(e)
    return


def delete_user(id: int):
    db: Session = next(get_db())
    try:
        db.query(User).filter(User.id == id).delete()
        db.commit()
        return True
    except Exception as e:
        print(e)
    return
