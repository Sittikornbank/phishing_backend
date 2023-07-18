from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from dotenv import load_dotenv
import bcrypt
import os
from schemas import GroupListModel, GroupDisplayModel, TargetModel, TargetDisplayModel
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


class GroupSummary(Base):
    __tablename__ = 'group_summaries'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(256))
    modified_date = Column(String(64))
    num_targets = Column(Integer)

# def validate_group(group):
#     if not group.name:
#         raise GroupValidationError("Group name not specified")
#     if not group.targets:
#         raise GroupValidationError("No targets specified")


# def insert_target_into_group(target, gid):
#     db: Session = SessionLocal()

#     if not target.email:
#         raise ValueError("No email address specified")

#     if db.query(Target).filter_by(email=target.email).count() > 0:
#         return

#     db.add(target)
#     db.commit()

#     db.add(Group_Target(group_id=gid, target_id=target.id))
#     db.commit()


# def get_targets(gid):
#     db: Session = SessionLocal()
#     return db.query(Target).join(Group_Target).filter(Group_Target.group_id == gid).all()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_gs(db: Session):
    return db.query(Group).all()


def get_g(db: Session, id: int):
    return db.query(Group).filter(Group.id == id).first()


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


# def create_group(group: GroupDisplayModel):
#     db: Session = next(get_db())
#     try:
#         targets = [
#             Target(
#                 first_name=target.first_name,
#                 last_name=target.last_name,
#                 email=target.email,
#                 position=target.position
#             )
#             for target in group.targets
#         ]

#         grou = Group(
#             name=group.name,
#             modified_date=group.modified_date,
#             targets=targets
#         )

#         db.add(grou)
#         db.commit()
#         db.refresh(grou)
#         return grou
#     except Exception as e:
#         print(e)
#     return

def update_target(targets: list[Target], updated_target: TargetDisplayModel) -> list[Target]:
    for target in targets:
        if target.first_name == updated_target.first_name and target.last_name == updated_target.last_name:
            # Update the target with the new data
            target.email = updated_target.email
            target.position = updated_target.position
            break
    return targets


# def update_group(id: int, updated_group: GroupDisplayModel):
#     db: Session = next(get_db())
#     try:
#         group = db.query(Group).filter(Group.id == id).first()

#         if not group:
#             raise ValueError("Group not found")

#         targets = update_target(group.targets)

#         group.name = updated_group.name
#         group.modified_date = updated_group.modified_date
#         group.targets = targets

#         db.commit()
#         db.refresh(group)
#         return group
#     except Exception as e:
#         print(e)
#     return
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
        c = db.query(Group).filter(Group.id == id).delete()
        db.commit()
        return c > 0
    except Exception as e:
        print(e)
    return
