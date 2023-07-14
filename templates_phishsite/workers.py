from models import Phishsite, get_phishsite_by_id, get_site_template_by_id
from dotenv import load_dotenv
from httpx import AsyncClient
from fastapi import HTTPException, status
from time import time
from datetime import datetime, timedelta
from schemas import EventContext, Event
import os
import jwt

load_dotenv()

SECRET = os.getenv("SECRET")
# rid, phishsite id, site template id
tasks: dict[str, tuple[int, int]] = dict()
tasks['abc'] = (4, 3)
tasks['hello'] = (5, 102)


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


def process_event(context: EventContext, wid: int):
    if context.ref_id in tasks and tasks[context.ref_id][0] == wid:
        script_dir = os.path.dirname(__file__)
        path = os.path.join(script_dir, f'log/{context.ref_id}.txt')
        with open(path, 'a') as f:
            f.write(
                f'[{datetime.now().isoformat()}]Event:{context.event_type.value} Campaign:{context.ref_id} Payload:{context.payload}\n')


def get_landing(context: EventContext, wid: int):
    if context.ref_id in tasks and tasks[context.ref_id][0] == wid:
        return get_site_template_by_id(tasks[context.ref_id][1])
