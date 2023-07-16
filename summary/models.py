from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
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
    name = Column(String(256))
    created_date = Column(DateTime(), default=datetime.now())
    completed_date = Column(DateTime(), default=datetime.now())
    templates_id = Column(Integer)
    status = Column(String(256))
    url = Column(String(256))
    smtp_id = Column(Integer)
    launch_date = Column(DateTime)
    send_by_date = Column(DateTime)

    # visible = Column(String(32), default=Visible.NONE)
    # owner_id = Column(Integer, default=None)
    # org_id = Column(Integer, default=None)


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    name = Column(String(256))
    modified_date = Column(DateTime(), default=datetime.now())

    # visible = Column(String(32), default=Visible.NONE)
    # owner_id = Column(Integer, default=None)
    # org_id = Column(Integer, default=None)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer)
    email = Column(String(256))
    time = Column(DateTime)
    message = Column(String(256))
    details = Column(String(256))

    # visible = Column(String(32), default=Visible.NONE)
    # owner_id = Column(Integer, default=None)
    # org_id = Column(Integer, default=None)


class Result(Base):
    __tablename__ = "result"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer)
    user_id = Column(Integer)
    r_id = Column(String(256))
    email = Column(String(256))
    first_name = Column(String(256))
    last_name = Column(String(256))
    status = Column(String(256), nullable=False)
    ip = Column(String(256))
    latitude = Column(Float)
    longitude = Column(Float)
    position = Column(String(256))
    send_date = Column(DateTime)
    reported = Column(Boolean)
    modified_date = Column(DateTime, default=datetime.now())

    visible = Column(String(32), default=Visible.NONE)
    owner_id = Column(Integer, default=None)
    org_id = Column(Integer, default=None)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_campaign():
    db: Session = next(get_db())
    try:
        return db.query(Campaign).all()
    except Exception as e:
        print(e)
    return


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
            created_date=camp.created_date,
            complate=camp.completed_date,
            template_id=camp.template_id,
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


def delete_campaign(db: Session, id: int):
    db: Session = next(get_db())
    try:
        db.query(Campaign).filter(Campaign.id == id).delete()
        db.commit()
    except Exception as e:
        print(e)
    return


def get_campaign_results_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(Campaign).filter(Campaign.id == id).first()
    except Exception as e:
        print(e)
    return


def get_campaign_summary_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(Campaign).filter(Campaign.id == id).first()
    except Exception as e:
        print(e)
    return


def get_campaign_complete_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(Campaign).filter(Campaign.id == id).first()
    except Exception as e:
        print(e)
    return


# class APIHandler:
#     def Campaigns_GET(self, user_id: int) -> List[Campaign]:
#         # Implement the logic to retrieve campaigns for the given user_id
#         pass

#     def Campaigns_POST(self, user_id: int, data: dict) -> Campaign:
#         # Implement the logic to create a new campaign for the given user_id using the provided data
#         pass

#     def Campaign_GET(self, user_id: int, campaign_id: int) -> Campaign:
#         # Implement the logic to retrieve the details of the specified campaign for the given user_id and campaign_id
#         pass

#     def Campaign_DELETE(self, user_id: int, campaign_id: int) -> None:
#         # Implement the logic to delete the specified campaign for the given user_id and campaign_id
#         pass

#     def CampaignResults_GET(self, user_id: int, campaign_id: int) -> CampaignResults:
#         # Implement the logic to retrieve the results of the specified campaign for the given user_id and campaign_id
#         pass

#     def CampaignSummary_GET(self, user_id: int, campaign_id: int) -> CampaignSummary:
#         # Implement the logic to retrieve the summary of the specified campaign for the given user_id and campaign_id
#         pass

#     def CampaignComplete_GET(self, user_id: int, campaign_id: int) -> None:
#         # Implement the logic to mark the specified campaign as complete for the given user_id and campaign_id
#         pass
