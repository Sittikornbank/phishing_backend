from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException
import os
from schemas import GroupModel, GroupFormModel, CampaignModel

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URI')
ORG_1_DB_URL = os.getenv('ORGANIZATION_DB_1')
ORG_2_DB_URL = os.getenv('ORGANIZATION_DB_2')

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

ORGANIZATION_DB: dict[int, tuple[Engine, Session]] = dict()


def init_org_db():
    global ORGANIZATION_DB
    ORGANIZATION_DB[0] = (engine, SessionLocal)

    engine1 = create_engine(ORG_1_DB_URL, echo=False)
    engine2 = create_engine(ORG_2_DB_URL, echo=False)

    ORGANIZATION_DB[1] = (engine1, sessionmaker(
        autocommit=False, autoflush=False, bind=engine1))
    ORGANIZATION_DB[2] = (engine2, sessionmaker(
        autocommit=False, autoflush=False, bind=engine2))

    for value in ORGANIZATION_DB.values():
        if value[0] != engine:
            Base.metadata.create_all(bind=value[0])


class GroupIndex(Base):
    __tablename__ = "group_indexs"

    group_id = Column(Integer, primary_key=True,
                      index=True, autoincrement=True)
    org_id = Column(Integer, primary_key=True)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(256))
    modified_date = Column(String(64))
    user_id = Column(Integer)
    org_id = Column(Integer)
    targets = relationship(
        "Target", secondary="group_targets", back_populates="groups")


class Group_Target(Base):
    __tablename__ = "group_targets"

    group_id = Column(Integer, ForeignKey(
        "groups.id", ondelete="CASCADE"), primary_key=True)
    target_id = Column(Integer, ForeignKey(
        "targets.id", ondelete="CASCADE"), primary_key=True)


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    firstname = Column(String(512))
    lastname = Column(String(512))
    email = Column(String(256), nullable=False)
    position = Column(String(256))
    department = Column(String(256))
    phonenumber = Column(String(16))


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    org_id = Column(Integer, default=None)
    name = Column(String(256))
    created_date = Column(DateTime(), default=datetime.now())
    completed_date = Column(DateTime(), default=None)
    templates_id = Column(Integer)
    group_id = Column(Integer, ForeignKey(
        "group_indexs.group_id", ondelete="SET NULL"))
    status = Column(String(32))
    smtp_id = Column(Integer)
    launch_date = Column(DateTime(), default=datetime.now())
    send_by_date = Column(DateTime(), default=None)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer)
    email = Column(String(256))
    time = Column(DateTime)
    message = Column(String(256))
    details = Column(JSON())


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer)
    user_id = Column(Integer)
    r_id = Column(String(256))
    email = Column(String(256))
    first_name = Column(String(256))
    last_name = Column(String(256))
    status = Column(String(256), nullable=False)
    ip = Column(String(64))
    latitude = Column(Float)
    longitude = Column(Float)
    position = Column(String(256))
    send_date = Column(DateTime, default=None)
    open_date = Column(DateTime, default=None)
    click_date = Column(DateTime, default=None)
    submit_date = Column(DateTime, default=None)
    report_date = Column(DateTime, default=None)
    modified_date = Column(DateTime, default=datetime.now())


def get_db(org_id: int = None):
    db: Session = None
    if org_id == None:
        db: Session = SessionLocal()
    elif org_id in ORGANIZATION_DB:
        db: Session = ORGANIZATION_DB[org_id][1]()
    try:
        yield db
    finally:
        db.close()


def get_groups_no_org(page: int | None = None, size: int | None = None):
    db: Session = next(get_db())


def get_groups_by_org(org_id: int, page: int | None = None, size: int | None = None):
    db: Session = next(get_db())


def get_sum_group_no_org(page: int | None = None, size: int | None = None):
    db: Session = next(get_db())


def get_sum_group_by_org(org_id: int, page: int | None = None, size: int | None = None):
    db: Session = next(get_db())


def get_group_by_id(id: int, org_id: int | None):
    db: Session = next(get_db())


def count_group_by_user(user_id: int):
    db: Session = next(get_db())


def create_group(group_in: GroupModel, org_id: int | None, user_id: int):
    db: Session = next(get_db())


def update_group(id: int, group_in: GroupFormModel, org_id: int | None):
    db: Session = next(get_db())


def delete_group(id: int, group_in: GroupFormModel, org_id: int | None):
    db: Session = next(get_db())


def get_all_campaigns():
    db: Session = next(get_db())


def get_campaign_by_id(id: int):
    db: Session = next(get_db())


def get_campaigns_by_user(user_id: int):
    db: Session = next(get_db())


def get_campaigns_by_org(org_id: int):
    db: Session = next(get_db())


def count_campaign_by_user(user_id: int):
    db: Session = next(get_db())


def get_all_campaigns_sum():
    db: Session = next(get_db())


def get_campaign_sum_by_id(id: int):
    db: Session = next(get_db())


def get_campaigns_sum_by_user(user_id: int):
    db: Session = next(get_db())


def get_campaigns_result_by_org(org_id: int):
    db: Session = next(get_db())


def get_all_campaigns_result():
    db: Session = next(get_db())


def get_campaign_result_by_id(id: int):
    db: Session = next(get_db())


def get_campaigns_result_by_user(user_id: int):
    db: Session = next(get_db())


def get_campaigns_sum_by_org(org_id: int):
    db: Session = next(get_db())


def create_campaign(cam_in: CampaignModel):
    db: Session = next(get_db())


def update_campaign(id: int, cam_in: dict):
    db: Session = next(get_db())


def delete_campaign(id: int):
    db: Session = next(get_db())
