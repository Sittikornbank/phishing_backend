from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from datetime import datetime
from schemas import (Visible, CampaignModel, CampaignFormModel,
                     CampaignDisplayModel, CampaignListModel)
import os


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    name = Column(String(2048))
    create_date = Column(DateTime(), default=datetime.now())
    complate = Column(DateTime(), default=datetime.now())
    templates_id = Column(Integer)
    status = Column(String(2048))
    url = Column(String(2048))
    smtp_id = Column(Integer)
    launch_date = Column(DateTime)
    send_by_date = Column(DateTime)
    visible = Column(String(32), default=Visible.NONE)
    owner_id = Column(Integer, default=None)
    org_id = Column(Integer, default=None)


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    name = Column(String(2048))
    modified_date = Column(DateTime(), default=datetime.now())
    visible = Column(String(32), default=Visible.NONE)
    owner_id = Column(Integer, default=None)
    org_id = Column(Integer, default=None)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer)
    email = Column(String(2048))
    time = Column(DateTime)
    message = Column(String(2048))
    details = Column(String(2048))
    visible = Column(String(32), default=Visible.NONE)
    owner_id = Column(Integer, default=None)
    org_id = Column(Integer, default=None)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all_campaigns(page: int | None = None, size: int | None = None):
    db: Session = next(get_db())
    try:
        if not size or size < 0:
            size = 25
        if not page or page < 0:
            page = 1
        camp = db.query(Campaign).offset(size*(page-1)).all()
        count = db.query(Campaign).count()
        return CampaignListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 campaign=camp)
    except Exception as e:
        print(e)
    return CampaignListModel()


def get_campaign_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(Campaign).filter(Campaign.id == id).first()
    except Exception as e:
        print(e)
    return


def create_campaign(camp: CampaignModel):
    db: Session = next(get_db())
    try:
        camp = Campaign(
            user_id=camp.user_id,
            name=camp.name,
            create_date=camp.create_date,
            complate=camp.complate,
            templates_id=camp.templates_id,
            status=camp.status,
            url=camp.url,
            smtp_id=camp.smtp_id,
            launch_date=camp.launch_date,
            send_by_date=camp.send_by_date,
            visible=camp.visible,
            owner_id=camp.owner_id,
            org_id=camp.org_id
        )
        db.add(camp)
        db.commit()
        db.refresh(camp)
        return camp
    except Exception as e:
        print(e)
    return


def update_site_temp(id: int, camp_in: dict):
    db: Session = next(get_db())
    try:
        if camp_in:
            camp_in['create_date'] = datetime.now()
            db.query(Campaign).filter(
                Campaign.id == id).update(camp_in)
            db.commit()
            return get_campaign_by_id(id)
    except Exception as e:
        print(e)
    return
