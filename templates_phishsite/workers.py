from models import Phishsite, get_phishsite_by_id, get_site_template_by_id
from dotenv import load_dotenv
from httpx import AsyncClient
from fastapi import HTTPException, status
from time import time
from datetime import datetime, timedelta
from schemas import EventContext, Event
import os

load_dotenv()

SECRET = os.getenv("SECRET")
# rid, phishsite id, site template id
tasks: dict[str, tuple[int, int]] = dict()


async def ping_worker_by_id(id: int):
    worker = get_phishsite_by_id(id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    async with AsyncClient() as client:
        try:
            res = await client.post(worker.uri+'/ping', json={'ref_key': worker.secret_key, "ping": int(time()*1000)})
            if res.status_code == 201:
                res = res.json()
                return {'sucess': True, 'ping': int(time()*1000)-res['pong']}
        except Exception as e:
            print(e)
            return {'sucess': False}


async def ping_worker(worker: Phishsite):
    if not worker:
        return {'sucess': False}
    async with AsyncClient() as client:
        try:
            res = await client.post(worker.uri+'/ping', json={'ref_key': worker.secret_key, "ping": int(time()*1000)})
            if res.status_code == 201:
                res = res.json()
                return {'sucess': True, 'ping': int(time()*1000)-res['pong']}
        except Exception as e:
            print(e)
            return {'sucess': False}


def code(lang: str):
    if lang == 'python':
        return '''print("hello world!")'''
    if lang == 'fastapi':
        return '''print("hello world!")'''


def process_event(context: EventContext):
    if context.ref_id in tasks:
        print(
            f'Event:{context.event_type}, Campaign:{context.ref_id}, Payload:{context.payload}')


def get_landing(context: EventContext):
    if context.ref_id in tasks:
        return get_site_template_by_id(tasks[context.ref_id][1])
