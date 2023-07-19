from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from dotenv import load_dotenv
import bcrypt
import os
from schemas import GroupListModel, GroupDisplayModel, TargetModel, TargetDisplayModel, Visible, CampaignModel
import email.utils as email_utils

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(256))
    modified_date = Column(String(64))
    # visible = Column(String(32), default=VISIBLE.NONE)

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
    first_name = Column(String(256))
    last_name = Column(String(256))
    email = Column(String(256))
    position = Column(String(256))

    groups = relationship(
        "Group", secondary="group_targets", back_populates="targets")

    def format_address(self):
        addr = self.email
        if self.first_name and self.last_name:
            name = f"{self.first_name} {self.last_name}"
            addr = email_utils.formataddr((name, self.email))
        return addr


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
    __tablename__ = "results"

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


def get_all_group(page: int | None = None, size: int | None = None):
    db: Session = next(get_db())
    try:
        if not size or size < 0:
            size = 25
        if not page or page < 0:
            page = 1
        gs = db.query(Group).offset(size*(page-1)).all()
        count = db.query(Group).count()
        return GroupListModel(count=count,
                              page=page,
                              limit=size,
                              last_page=(count//size)+1,
                              group=gs)
    except Exception as e:
        print(e)
    return GroupListModel()


def get_group_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(Group).filter(Group.id == id).first()
    except Exception as e:
        print(e)
    return


def create_targets(targets: list[TargetDisplayModel]) -> list[Target]:
    return [
        Target(
            first_name=target.first_name,
            last_name=target.last_name,
            email=target.email,
            position=target.position
        )
        for target in targets
    ]


def create_group(group: GroupDisplayModel):
    db: Session = next(get_db())
    try:
        targets = create_targets(group.targets)

        group = Group(
            name=group.name,
            modified_date=group.modified_date,
            targets=targets
        )

        db.add(group)
        db.commit()
        db.refresh(group)
        return group
    except Exception as e:
        print(e)
    return


def update_group(temp_in: dict, id: int):
    db: Session = next(get_db())
    try:
        if temp_in:
            temp_in['modified_date'] = datetime.now()

            # Separate the update for name and modified_date from the targets
            if 'targets' in temp_in:
                del temp_in['targets']

            db.query(Group).filter(Group.id == id).update(temp_in)
            db.commit()
            return get_group_by_id(id)
    except Exception as e:
        print(e)
    return


def delete_group(id: int):
    db: Session = next(get_db())
    try:
        # Get the group to be deleted
        group = db.query(Group).filter(Group.id == id).first()

        # Check if the group exists
        if not group:
            return False

        # Delete associated targets from the group
        for target in group.targets:
            db.delete(target)
        # Delete the group
        db.delete(group)
        db.commit()
        return True

    except Exception as e:
        print(e)
    return False

# ------------------------- Campaign -----------------------------------#


def get_campaign():
    db: Session = next(get_db())
    try:
        return db.query(Campaign).all()
    except Exception as e:
        print(e)
    return


def get_all_campaign(page: int | None = None, size: int | None = None):
    db: Session = next(get_db())
    try:
        if not size or size < 0:
            size = 25
        if not page or page < 0:
            page = 1
        gs = db.query(Campaign).offset(size*(page-1)).all()
        count = db.query(Campaign).count()
        return GroupListModel(count=count,
                              page=page,
                              limit=size,
                              last_page=(count//size)+1,
                              campaing=gs)
    except Exception as e:
        print(e)
    return GroupListModel()


def get_campaign_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(Campaign).filter(Campaign.id == id).first()
    except Exception as e:
        print(e)
    return

    return


def create_campaign(gs: CampaignModel):
    db: Session = next(get_db())
    try:
        campai = Campaign(
            user_id=gs.user_id,
            name=gs.name,
            templates_id=gs.templates_id,
            status=gs.status,
            url=gs.url,
            smtp_id=gs.smtp_id
        )
        db.add(campai)
        db.commit()
        db.refresh(campai)
    except Exception as e:
        print(e)
    return


def delete_campaign(id: int):
    db: Session = next(get_db())
    try:
        c = db.query(Campaign).filter(Campaign.id == id).delete()
        db.commit()
        return c > 0
    except Exception as e:
        print(e)
    return
