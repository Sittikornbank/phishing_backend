from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy import create_engine, Engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException
from datetime import datetime
from dotenv import load_dotenv
import os
from stat_ import get_res, get_res_ex
from schemas import (GroupModel, CampaignListModel, CampaignModel,
                     GroupListModel, GroupSumListModel, TargetModel,
                     EVENT, Summary, Status, EventModel, CampaignSummaryModel,
                     CampaignSumListModel, EVENT, ResultModel)

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URI')
ORG_1_DB_URL = os.getenv('ORGANIZATION_DB_1')
ORG_2_DB_URL = os.getenv('ORGANIZATION_DB_2')

engine = create_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

ORGANIZATION_DB: dict[int, tuple[Engine, Session]] = dict()


def init_org_db():
    global ORGANIZATION_DB
    ORGANIZATION_DB[0] = (engine, SessionLocal)

    # engine1 = create_engine(ORG_1_DB_URL, echo=False)
    # engine2 = create_engine(ORG_2_DB_URL, echo=False)

    # ORGANIZATION_DB[1] = (engine1, sessionmaker(
    #     autocommit=False, autoflush=False, bind=engine1))
    # ORGANIZATION_DB[2] = (engine2, sessionmaker(
    #     autocommit=False, autoflush=False, bind=engine2))

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
    status = Column(String(32), default=Status.IDLE)
    smtp_id = Column(Integer)
    launch_date = Column(DateTime(), default=None)
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
    firstname = Column(String(256), default='')
    lastname = Column(String(256), default='')
    department = Column(String(256), default='')
    position = Column(String(256), default='')
    status = Column(String(256), default=EVENT.LAUNCH)
    ip = Column(String(64), default='')
    latitude = Column(Float, default=0)
    longitude = Column(Float, default=0)
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


def get_groups_by_user(user_id: int, page: int | None = None, size: int | None = None):
    db: Session = next(get_db())
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


def get_sum_groups_by_id(id: int):
    group = get_group_by_id(id)
    if group:
        setattr(group, 'num_targets', len(group.targets))
        return group
    return


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


def create_group(group_in: GroupModel):
    group_index = create_group_index(group_in.org_id)
    if not group_index:
        return
    db: Session = next(get_db(group_in.org_id))
    try:
        group = Group(
            id=group_index.group_id,
            name=group_in.name,
            modified_date=group_in.modified_date,
            user_id=group_in.user_id,
            org_id=group_in.org_id)
        targets = [
            Target(
                firstname=t.firstname,
                lastname=t.lastname,
                email=t.email,
                position=t.position,
                department=t.department,
                phonenumber=t.phonenumber,
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


def update_group(id: int, group_in: dict, add_targets: list[TargetModel] | None,
                 remove_targets: list[int] | None, org_id: int | None, max_target: int = -1):
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
            if max_target > 0 and db.query(Target).filter(
                    Target.group_id == group.id).count() > max_target:
                raise HTTPException(
                    status_code=403, detail='Targets more than Max allow')
            group.modified_date = datetime.now()
        if group_in:
            group.modified_date = datetime.now()
            group.name = group_in['name']

        if group and (remove_targets or add_targets or group_in):
            db.add(group)
            db.commit()
            db.refresh(group)
            return group

    except HTTPException as e:
        raise e
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


def get_campaign_summary(campaign_id: int, org_id: int | None, group_id: int | None):
    summary = Summary()
    if group_id:
        g = get_sum_groups_by_id(group_id)
        if g:
            summary.total = g.num_targets

    db: Session = next(get_db(org_id))
    try:
        results = db.query(Event.message, func.count()).filter(Event.campaign_id ==
                                                               campaign_id).group_by(Event.message).all()

        for result in results:
            if result._data[0] == EVENT.SEND:
                summary.sent = result._data[1]
            elif result._data[0] == EVENT.OPEN:
                summary.open = result._data[1]
            elif result._data[0] == EVENT.CLICK:
                summary.click = result._data[1]
            elif result._data[0] == EVENT.SUBMIT:
                summary.submit = result._data[1]
            elif result._data[0] == EVENT.REPORT:
                summary.report = result._data[1]
            elif result._data[0] == EVENT.FAIL:
                summary.fail = result._data[1]
        return summary
    except Exception as e:
        print(e)
    return


def get_all_campaigns_sum(page: int | None = None, size: int | None = None):
    camp_list = get_all_campaigns(page=page, size=size)
    campaigns = [
        CampaignSummaryModel(id=c.id,
                             name=c.name,
                             create_date=c.create_date,
                             status=c.status,
                             stats=get_campaign_summary(c.id, org_id=c.org_id, group_id=c.group_id))

        for c in camp_list.campaigns
    ]
    camp_list = CampaignSumListModel(count=camp_list.count,
                                     page=camp_list.page,
                                     last_page=camp_list.last_page,
                                     campaigns=campaigns)
    return camp_list


def get_campaign_sum_by_id(id: int):
    c = get_campaign_by_id(id)
    if not c:
        return
    camp = CampaignSummaryModel(id=c.id,
                                name=c.name,
                                created_date=c.created_date,
                                status=c.status,
                                stats=get_campaign_summary(c.id, org_id=c.org_id, group_id=c.group_id))
    return camp


def get_campaigns_sum_by_user(user_id: int, page: int | None = None, size: int | None = None):
    camps = get_campaigns_by_user(user_id=user_id, page=page, size=size)
    for camp in camps.campaigns:
        summary = get_campaign_summary(
            camp.id, org_id=camp.org_id, group_id=camp.group_id)
        setattr(camp, 'stats', summary)
    return camps


def get_campaigns_sum_by_org(org_id: int, page: int | None = None, size: int | None = None):
    camps = get_campaigns_by_user(org_id=org_id, page=page, size=size)
    for camp in camps.campaigns:
        summary = get_campaign_summary(
            camp.id, org_id=camp.org_id, group_id=camp.group_id)
        setattr(camp, 'stats', summary)
    return camps


def get_campaign_result_by_id(id: int):
    camp = get_campaign_by_id(id)
    if not camp:
        return
    db: Session = next(get_db(camp.org_id))
    try:
        results = db.query(Result).filter(Result.campaign_id == id).all()
        events = db.query(Event).filter(Event.campaign_id == id).all()
        analy, stat = get_res([ResultModel(**r.__dict__).dict()
                              for r in results])
        setattr(camp, 'results', analy)
        setattr(camp, 'timelines', events)
        setattr(camp, 'statistics', stat)
        return camp
    except Exception as e:
        print(e)
    return


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


def add_event(event: EventModel):
    camp = get_campaign_by_id(event.campaign_id)
    if not camp:
        return
    if camp.status == Status.COMPLETE:
        return
    db: Session = next(get_db(camp.org_id))
    try:
        event = Event(
            campaign_id=event.campaign_id,
            email=event.email,
            time=event.time,
            message=event.message,
            details=event.details
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        print(e)
    return


def add_results(data: dict, camp: Campaign):
    if not ('ref_key' in data) or not ('targets' in data):
        return False
    db: Session = next(get_db(camp.org_id))
    try:
        targets = [
            Result(
                campaign_id=camp.id,
                user_id=camp.user_id,
                r_id=data['ref_key']+t['ref'],
                email=t['email'],
                firstname=t['firstname'],
                lastname=t['lastname'],
                department=t['department'],
                position=t['position']
            ) for t in data['targets']
        ]
        db.add_all(targets)
        db.commit()
        return True
    except Exception as e:
        print(e)
    return False


def update_result(org_id: int, event: EventModel):
    db: Session = next(get_db(org_id))
    try:
        result = db.query(Result).filter(Result.campaign_id ==
                                         event.campaign_id, Result.r_id == event.r_id).first()
        if not result:
            raise Exception('result not found')

        is_update = False
        if event.message == EVENT.SEND and result.send_date == None:
            result.send_date = event.time
            result.status = EVENT.SEND
            is_update = True
        elif event.message == EVENT.OPEN and result.open_date == None:
            result.open_date = event.time
            result.status = EVENT.OPEN
            is_update = True
        elif event.message == EVENT.CLICK and result.click_date == None:
            result.click_date = event.time
            result.status = EVENT.CLICK
            is_update = True
        elif event.message == EVENT.SUBMIT and result.submit_date == None:
            result.submit_date = event.time
            result.status = EVENT.SUBMIT
            is_update = True
        elif event.message == EVENT.REPORT and result.report_date == None:
            result.report_date = event.time
            is_update = True
        elif event.message == EVENT.FAIL and result.send_date == None:
            result.status = EVENT.FAIL
            is_update = True

        if is_update:
            result.modified_date = event.time
            db.add(result)
            db.commit()
            return True
    except Exception as e:
        print(e)
    return False


def get_all_result():
    db: Session = next(get_db())
    try:
        return db.query(Result).all()
    except Exception as e:
        print(e)
    return


def get_result_by_id(id: int):
    db: Session = next(get_db())
    try:
        return db.query(Result).filter(Result.id == id).first()
    except Exception as e:
        print(e)
    return


def count_status(all_results):
    status_count = {
        "sent": 0,
        "open": 0,
        "click": 0,
        "submit": 0,
        "report": 0,
        "total": 0,  # เพิ่มสถานะ total เพื่อนับทั้งหมด
        "fail": 0
    }

    for item in all_results:
        if item.send_date:
            status_count["sent"] += 1
            status_count["total"] += 1  # เพิ่มการนับทั้งหมดที่ส่งไป
        else:
            # เพิ่มการนับทั้งหมดไม่ว่าจะส่งหรือไม่ส่ง
            status_count["fail"] += 1
            status_count["total"] += 1
        if item.open_date:
            status_count["open"] += 1
        if item.click_date:
            status_count["click"] += 1
        if item.submit_date:
            status_count["submit"] += 1
        if item.report_date:
            status_count["report"] += 1

    result_summary = {
        "total": status_count["total"],
        "sent": status_count["sent"],
        "open": status_count["open"],
        "click": status_count["click"],
        "submit": status_count["submit"],
        "report": status_count["report"],
        "fail": status_count["fail"]
    }
    return result_summary


# use orgigtion get_campaign_result_by_id


def get_campaign_result_by_id_for_export(id: int):
    camp = get_campaign_by_id(id)
    if not camp:
        return
    db: Session = next(get_db(camp.org_id))
    try:
        results = db.query(Result).filter(Result.campaign_id == id).all()
        events = db.query(Event).filter(Event.campaign_id == id).all()
        # chang data to dict for export
        analy, stat = get_res_ex([ResultModel(**r.__dict__).dict()
                                  for r in results])
        timelines = ([EventModel(**r.__dict__).dict()
                      for r in events])
        return analy, timelines, stat
    except Exception as e:
        print(e)
    return
