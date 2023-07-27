from models import Phishsite, get_phishsite_by_id, get_site_template_by_id
from dotenv import load_dotenv
from httpx import AsyncClient
from fastapi import HTTPException, status
from time import time
from datetime import datetime, timedelta
from schemas import EventContext, Event, Task, AuthContext, TemplateReqModel, SiteModel
import os
import jwt

load_dotenv()

SECRET = os.getenv("SECRET")
CALLBACK_URI = os.getenv("CALLBACK_URI")
API_KEY = os.getenv("API_KEY")

tasks: dict[str, Task] = dict()


def create_token(worker: Phishsite):
    return jwt.encode({"id": worker.id,
                       "exp": datetime.utcnow() + timedelta(minutes=3)},
                      worker.secret_key, algorithm="HS256")


def validate_token(ref_key: str):
    data = jwt.decode(ref_key, options={"verify_signature": False})
    if 'id' not in data:
        return -1
    worker = get_phishsite_by_id(data['id'])
    if not worker:
        return -1
    try:
        jwt.decode(ref_key, worker.secret_key, algorithms=["HS256"])
        return worker.id
    except Exception as e:
        print(e)
    return -1


async def ping_worker_by_id(id: int):
    worker = get_phishsite_by_id(id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    return await ping_worker(worker)


async def ping_worker(worker: Phishsite):
    if not worker:
        return {'sucess': False}
    async with AsyncClient() as client:
        try:
            ref_key = create_token(worker)
            ping = int(time()*1000)
            res = await client.post(worker.uri+'/ping', json={'ref_key': ref_key, "ping": ping})
            if res.status_code == 201:
                res = res.json()
                if ping == res['pong']:
                    return {'sucess': True, 'ping': int(time()*1000)-ping}
        except Exception as e:
            print(e)
    return {'sucess': False}


def code(lang: str):
    if lang == 'python':
        return '''print("hello world!")'''
    if lang == 'fastapi':
        return '''print("hello world!")'''


async def update_status(data: dict):
    print(data)
    async with AsyncClient() as client:
        try:
            data.update({'sender': 'site'})
            header = {'Authorization': f'Bearer {API_KEY}'}
            res = await client.post(CALLBACK_URI, json=data, headers=header)
            if res.status_code == 200:
                return True
        except Exception as e:
            print(e)
    return False


async def process_event(context: EventContext, wid: int):
    if context.ref_key in tasks and context.ref_id in tasks[context.ref_key].ref_ids and \
            tasks[context.ref_key].worker_id == wid and time() > tasks[context.ref_key].start_at:
        await update_status(context.dict())


def get_landing(context: EventContext, wid: int):
    if context.ref_key in tasks and context.ref_id in tasks[context.ref_key].ref_ids and \
            tasks[context.ref_key].worker_id == wid and time() > tasks[context.ref_key].start_at:
        try:
            return tasks[context.ref_key].site
        except:
            return None


def get_dotpng(context: EventContext, wid: int):
    return context.ref_key in tasks and context.ref_id in tasks[context.ref_key].ref_ids and \
        tasks[context.ref_key].worker_id == wid and time(
    ) > tasks[context.ref_key].start_at


def add_landing_task(req: TemplateReqModel, site: SiteModel, auth: AuthContext):
    if site.phishsite_id == None:
        return False
    task = Task(ref_key=req.ref_key, ref_ids=req.ref_ids,
                site=site, worker_id=site.phishsite_id, start_at=req.start_at,
                org_id=auth.organization, user_id=auth.id)
    if req.ref_key in tasks:
        return False
    tasks[req.ref_key] = task
    return True


def get_task_by_ref(ref_key: str):
    if not ref_key in tasks:
        return
    return tasks[ref_key]


def get_all_tasks():
    return list(tasks.values())


def remove_task(ref_key: str):
    if ref_key in tasks:
        tasks.pop(ref_key)
