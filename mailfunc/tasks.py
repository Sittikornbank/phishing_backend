import threading
import asyncio
import os
import time
import jinja2
import binascii
from dotenv import load_dotenv
from schemas import Target, TaskModel, Status, TaskStatModel, EventType
from httpx import AsyncClient
import smtplib
import string
from models import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
CALLBACK_URI = os.getenv('CALLBACK_URI')
API_KEY = os.getenv('API_KEY')
environment = jinja2.Environment()

semaphore = threading.Semaphore(5)
dict_mutex = threading.Lock()
tasks_dict: dict[str, tuple[TaskStatModel, threading.Event]] = dict()


def add_task_to_dict(id: str, event: threading.Event, task: TaskStatModel):
    global tasks_dict
    with dict_mutex:
        tasks_dict[id] = (task, event)
        return True


def remove_task_from_dict(task_id: str):
    global tasks_dict
    with dict_mutex:
        if task_id in tasks_dict:
            tasks_dict.pop(task_id)
            return True
    return False


def get_task_by_ref(task_id: str):
    with dict_mutex:
        if task_id in tasks_dict:
            return tasks_dict[task_id][0]


def modify_status_dict(task_id: str, status: Status = Status.IDLE, sent: int = 0, fail: int = 0):
    global tasks_dict
    with dict_mutex:
        if task_id in tasks_dict:
            if sent:
                tasks_dict[task_id][0].sent = sent
            if fail:
                tasks_dict[task_id][0].fail = fail
            if status != Status.IDLE:
                tasks_dict[task_id][0].status = status


def get_running_task():
    with dict_mutex:
        return [tasks_dict[t][0] for t in tasks_dict]


def stop_running_task(task_id: str):
    with dict_mutex:
        if task_id in tasks_dict:
            tasks_dict[task_id][0].status = Status.STOP
            tasks_dict[task_id][1].clear()


async def update_status(data: dict):
    # print(data)
    async with AsyncClient() as client:
        try:
            data.update({'sender': 'email'})
            header = {'Authorization': f'Bearer {API_KEY}'}
            res = await client.post(CALLBACK_URI, json=data, headers=header)
            if res.status_code == 200:
                return True
        except Exception as e:
            print(e)
    return False


def random_url_parameter(ref: str):
    char = string.ascii_lowercase+string.ascii_uppercase+string.digits
    ran = [binascii.hexlify(os.urandom(32)).decode('utf-8'),
           binascii.hexlify(os.urandom(28)).decode('utf-8'),
           binascii.hexlify(os.urandom(16)).decode('utf-8')]
    return f"?id={ran[0]}&verification={ran[1]}&ref={ref}&tid={ran[2]}"


def render_template(template: str, target: Target, ref_key: str, base_url: str):
    ref = ref_key + target.ref
    ref = random_url_parameter(ref)
    tracking = base_url + "/image/dot.png" + ref
    base_url = base_url + ref
    temp = environment.from_string(template)
    data = target.dict(exclude_none=True, exclude_unset=True)
    data.update({'tracking': tracking, 'base_url': base_url})
    return temp.render(data)


def send_email(to_email: str, subject: str, message: str, sender: str, att: list[str], smtp: SMTP):
    try:
        msg = MIMEMultipart()
        if sender:
            msg['From'] = sender
        else:
            msg['From'] = smtp.username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))

        host, port = smtp.host.split(':')
        with smtplib.SMTP(host, int(port)) as server:
            server.starttls()
            server.login(smtp.username, smtp.password)
            server.sendmail(smtp.username, to_email, msg.as_string())
            return True
    except Exception as e:
        print(e)
    return False


def send_test_email(smtp: SMTP):
    return send_email(smtp.username, "Test Email Working!", "<h1>It's working</h1>", smtp.username, [], smtp)


async def send_email_task(task: TaskModel, smtp: SMTP, semaphore: threading.Semaphore, event: threading.Event):
    with semaphore:
        task.status = Status.RUNNING
        task.sent = 0
        task.fail = 0
        if len(task.targets) != 0:
            delay = task.duration/len(task.targets)
        else:
            delay = 0
        # await update_status(
        #     {'task_id': task.task_id, 'status': task.status, 'sent': 0})
        modify_status_dict(task_id=task.task_id, status=Status.RUNNING)
        for i, t in enumerate(task.targets):
            if not divide_sleep(delay, event):
                break
            sub = render_template(
                task.subject, t, ref_key=task.task_id, base_url=task.base_url)
            msg = render_template(
                task.html, t, ref_key=task.task_id, base_url=task.base_url)
            if send_email(t.email, sub, msg, task.sender, task.attachments, smtp):
                task.sent += 1
                modify_status_dict(task_id=task.task_id, sent=task.sent)
                await update_status(
                    {'ref_key': task.task_id, 'ref_id': t.ref, 'event_type': EventType.SEND, 'payload': None})
            else:
                task.fail += 1
                modify_status_dict(task_id=task.task_id, fail=task.fail)
                await update_status(
                    {'ref_key': task.task_id, 'ref_id': t.ref, 'event_type': EventType.FAIL, 'payload': None})
        # if task.sent == len(task.targets):
        task.status = Status.COMPLETE
        # await update_status(
        #     {'task_id': task.task_id, 'status': task.status, 'sent': task.sent})
        remove_task_from_dict(task.task_id)


def task_warpper(task: TaskModel, smtp: SMTP, sem: threading.Semaphore, event: threading.Event):
    asyncio.run(send_email_task(task, smtp, sem, event))


async def create_and_start_task(task: TaskModel, smtp: SMTP):
    try:
        event = threading.Event()
        t = threading.Thread(target=task_warpper, args=(
            task, smtp, semaphore, event))
        event.set()
        t.start()
        add_task_to_dict(id=task.task_id, event=event,
                         task=TaskStatModel(ref_key=task.task_id,
                                            total=len(task.targets),
                                            user_id=task.auth.id,
                                            org_id=task.auth.organization))
        return t.is_alive()
    except Exception as e:
        print(e)
    return False


def divide_sleep(duration: float, event: threading.Event):
    if duration < 0:
        duration = 0
    if not event.wait(timeout=3):
        return False
    if duration < 60:
        time.sleep(duration)
        return event.wait(timeout=3)
    step = int(duration // 60)
    rem = duration % 60
    for i in range(step):
        time.sleep(60)
        if not event.wait(timeout=3):
            return False
    time.sleep(rem)
    return event.wait(timeout=3)
