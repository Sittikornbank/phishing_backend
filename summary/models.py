from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy import create_engine, Engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from dotenv import load_dotenv
import os
from schemas import (GroupModel, CampaignListModel, CampaignModel,
                     GroupListModel, GroupSumListModel, TargetModel,
                     EVENT, Summary, Status)

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

    targets = relationship("Target")


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    firstname = Column(String(512))
    lastname = Column(String(512))
    email = Column(String(256), nullable=False)
    position = Column(String(256))
    department = Column(String(256))
    phonenumber = Column(String(16))
    group_id = Column(Integer, ForeignKey(
        "groups.id", ondelete="CASCADE"))

    group = relationship('Group', back_populates='targets')


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
    return get_groups_by_org(org_id=0, page=page, size=size)


def get_groups_by_org(org_id: int, page: int | None = None, size: int | None = None):
    db: Session = next(get_db(org_id))
    if not size or size < 0:
        size = 25
    if not page or page < 0:
        page = 1
    groups = list()
    count = 0
    try:
        groups = db.query(Group).filter(Group.org_id == org_id).limit(
            size).offset(size*(page-1)).all()
        count = db.query(Group).filter(Group.org_id == org_id).count()
        return GroupListModel(count=count, page=page,
                              last_page=(count//size)+1,
                              limit=size,
                              groups=groups)
    except Exception as e:
        print(e)
    return GroupListModel()


def get_sum_group_no_org(page: int | None = None, size: int | None = None):
    return get_sum_groups_by_org(org_id=0, page=page, size=size)


def get_sum_groups_by_org(org_id: int, page: int | None = None, size: int | None = None):
    db: Session = next(get_db(org_id))
    if not size or size < 0:
        size = 25
    if not page or page < 0:
        page = 1
    groups = list()
    count = 0
    try:
        groups = db.query(Group).limit(size).offset(size*(page-1)).all()
        count = db.query(Group).count()
        for g in groups:
            setattr(g, 'num_targets', len(g.targets))
        return GroupSumListModel(count=count, page=page,
                                 last_page=(count//size)+1,
                                 limit=size,
                                 groups=groups)
    except Exception as e:
        print(e)
    return GroupSumListModel()


def get_sum_groups_by_user(user_id: int, org_id: int | None, page: int | None = None, size: int | None = None):
    db: Session = next(get_db(org_id))
    if not size or size < 0:
        size = 25
    if not page or page < 0:
        page = 1
    groups = list()
    count = 0
    try:
        groups = db.query(Group).filter(Group.user_id == user_id).limit(
            size).offset(size*(page-1)).all()
        count = db.query(Group).filter(Group.user_id == user_id).count()
        for g in groups:
            setattr(g, 'num_targets', len(g.targets))
        return GroupSumListModel(count=count, page=page,
                                 last_page=(count//size)+1,
                                 limit=size,
                                 groups=groups)
    except Exception as e:
        print(e)
    return GroupSumListModel()


def get_org_of_group(id: int):
    db: Session = next(get_db())
    try:
        g: GroupIndex = db.query(GroupIndex).filter(
            GroupIndex.group_id == id).first()
        if g:
            return g.org_id
    except Exception as e:
        print(e)
    return


def get_group_by_id(id: int):
    org_id = get_org_of_group(id)
    if org_id == None:
        return
    db: Session = next(get_db(org_id))
    try:
        return db.query(Group).filter(Group.id == id).first()
    except Exception as e:
        print(e)
    return


def count_groups_by_user(user_id: int, org_id: int):
    db: Session = next(get_db(org_id))
    try:
        count = db.query(Group).filter(Group.user_id == user_id).count()
        return count
    except Exception as e:
        print(e)
    return 0


def create_group_index(org_id: int):
    db: Session = next(get_db())
    try:
        group_index = GroupIndex(
            org_id=org_id
        )
        db.add(group_index)
        db.commit()
        db.refresh(group_index)
        return group_index
    except Exception as e:
        print(e)
    return


def delete_group_index(id: int):
    db: Session = next(get_db())
    try:
        c = db.query(GroupIndex).filter(GroupIndex.id == id).delete()
        return c > 0
    except Exception as e:
        print(e)
    return


def create_group(group_in: GroupModel, org_id: int | None, user_id: int):
    group_index = create_group_index(org_id)
    if not group_index:
        return
    db: Session = next(get_db(org_id))
    try:
        group = Group(
            id=group_index.group_id,
            name=group_in.name,
            modified_date=group_in.modified_date,
            user_id=group_in.user_id,
            org_id=org_id)
        targets = [
            Target(
                firstname=t.firstname,
                lastname=t.lastname,
                email=t.email,
                position=t.position,
                department=t.department,
                phonenumber=t.phonenumber
            )
            for t in group_in.targets
        ]
        group.targets = targets
        db.add(group)
        db.commit()
        db.refresh(group)
        return group
    except Exception as e:
        print(e)
    return


def update_group(id: int, group_in: dict, add_targets: list[TargetModel],
                 remove_targets: list[int], org_id: int | None, max_target: int = 10):
    db: Session = next(get_db(org_id))
    try:
        group = db.query(Group).filter(
            Group.id == id, Group.org_id == org_id).first()
        if remove_targets:
            db.query(Target).filter(Target.group_id ==
                                    group.id, Target.id.in_(remove_targets)).delete()
            group.modified_date = datetime.now()
        if add_targets:
            targets = [
                Target(
                    firstname=t.firstname,
                    lastname=t.lastname,
                    email=t.email,
                    position=t.position,
                    department=t.department,
                    phonenumber=t.phonenumber
                ) for t in add_targets
            ]
            db.add_all(targets)
            group.targets.extend(targets)
            if db.query(Target).filter(Target.group_id == group.id).count() > max_target:
                raise Exception('target more tham maximium')
            group.modified_date = datetime.now()
        if group_in:
            group.modified_date = datetime.now()
            group.modified_date = group_in['name']

        if group and (remove_targets or add_targets or group_in):
            db.add(group)
            db.commit()
            db.refresh(group)
            return group

    except Exception as e:
        print(e)
    return


def delete_group(id: int, org_id: int | None):
    db: Session = next(get_db(org_id))
    try:
        c = db.query(Group).filter(Group.id == id,
                                   Group.org_id == org_id).delete()
        return c > 0
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
        campaigns = db.query(Campaign).limit(size).offset(size*(page-1)).all()
        count = db.query(Campaign).count()
        return CampaignListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 campaigns=campaigns)
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


def get_campaigns_by_user(user_id: int, page: int | None = None, size: int | None = None):
    db: Session = next(get_db())
    try:
        if not size or size < 0:
            size = 25
        if not page or page < 0:
            page = 1
        campaigns = db.query(Campaign).filter(
            Campaign.user_id == user_id).limit(size).offset(size*(page-1)).all()
        count = db.query(Campaign).filter(Campaign.user_id == user_id).count()
        return CampaignListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 campaigns=campaigns)
    except Exception as e:
        print(e)
    return


def get_campaigns_by_org(org_id: int, page: int | None = None, size: int | None = None):
    db: Session = next(get_db())
    try:
        if not size or size < 0:
            size = 25
        if not page or page < 0:
            page = 1
        campaigns = db.query(Campaign).filter(
            Campaign.org_id == org_id).limit(size).offset(size*(page-1)).all()
        count = db.query(Campaign).filter(Campaign.org_id == org_id).count()
        return CampaignListModel(count=count,
                                 page=page,
                                 limit=size,
                                 last_page=(count//size)+1,
                                 campaigns=campaigns)
    except Exception as e:
        print(e)
    return


def count_campaign_by_user(user_id: int):
    db: Session = next(get_db())
    try:
        return db.query(Campaign).filter(Campaign.user_id == user_id).count()
    except Exception as e:
        print(e)
    return 0


def get_campaign_summary(campaign_id: int, org_id: int | None):
    db: Session = next(get_db(org_id))
    try:
        results = db.query(Event.message, func.count()).filter(Event.campaign_id ==
                                                               campaign_id).group_by(Event.message).all()
        summary = Summary()
        for result in results:
            if result._data[0] == EVENT.SEND:
                summary.sent = result._data[1]
            elif result._data[0] == EVENT.OPEN:
                summary.opened = result._data[1]
            elif result._data[0] == EVENT.CLICK:
                summary.clicked = result._data[1]
            elif result._data[0] == EVENT.SUBMIT:
                summary.submitted = result._data[1]
            elif result._data[0] == EVENT.REPORT:
                summary.reported = result._data[1]
            elif result._data[0] == EVENT.FAIL:
                summary.failed = result._data[1]
        return summary
    except Exception as e:
        print(e)
    return


def get_all_campaigns_sum(page: int | None = None, size: int | None = None):
    camps = get_all_campaigns(page=page, size=size)
    for camp in camps.campaigns:
        summary = get_campaign_summary(camp.id, org_id=camp.org_id)
        setattr(camp, 'status', summary)
    return camps


def get_campaign_sum_by_id(id: int):
    camp = get_campaign_by_id(id)
    if not camp:
        return
    return get_campaign_summary(id, camp.org_id)


def get_campaigns_sum_by_user(user_id: int, page: int | None = None, size: int | None = None):
    camps = get_campaigns_by_user(user_id=user_id, page=page, size=size)
    for camp in camps.campaigns:
        summary = get_campaign_summary(camp.id, org_id=camp.org_id)
        setattr(camp, 'status', summary)
    return camps


def get_campaigns_sum_by_org(org_id: int, page: int | None = None, size: int | None = None):
    camps = get_campaigns_by_user(org_id=org_id, page=page, size=size)
    for camp in camps.campaigns:
        summary = get_campaign_summary(camp.id, org_id=camp.org_id)
        setattr(camp, 'status', summary)
    return camps


def get_campaign_result_by_id(id: int):
    db: Session = next(get_db())


def create_campaign(cam_in: CampaignModel):
    db: Session = next(get_db())
    try:
        campaign = Campaign(
            user_id=cam_in.user_id,
            org_id=cam_in.org_id,
            name=cam_in.name,
            created_date=cam_in.create_date,
            completed_date=None,
            templates_id=cam_in.templates_id,
            group_id=cam_in.group_id,
            status=Status.IDLE,
            smtp_id=cam_in.smtp_id,
            launch_date=cam_in.launch_date,
            send_by_date=cam_in.send_by_date
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign
    except Exception as e:
        print(e)
    return


def update_campaign(id: int, cam_in: dict):
    db: Session = next(get_db())
    try:
        db.query(Campaign).filter(Campaign.id == id).update(cam_in)
        db.commit()
        return get_campaign_by_id(id)
    except Exception as e:
        print(e)
    return


def delete_campaign(id: int):
    db: Session = next(get_db())
    try:
        c = db.query(Campaign).filter(Campaign.id == id).delete()
        return c > 0
    except Exception as e:
        print(e)
    return
