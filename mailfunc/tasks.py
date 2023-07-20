import threading
import asyncio
import os
import time
import jinja2
import binascii
from dotenv import load_dotenv
from schemas import Target, TaskModel, Status
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

tasks_dict = dict()


async def update_status(data: dict):
    print(data)
    async with AsyncClient() as client:
        try:
            data.update({'api_key': API_KEY})
            data.update({'timestamp': time.time()})
            res = await client.post(CALLBACK_URI, json=data)
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
    print(base_url)
    temp = environment.from_string(template)
    data = target.dict()
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


async def send_email_task(task: TaskModel, smtp: SMTP):
    task.status = Status.RUNNING
    task.sent = 0
    if len(task.targets) != 0:
        delay = task.duration/len(task.targets)
    else:
        delay = 0
    await update_status(
        {'task_id': task.task_id, 'status': task.status, 'sent': 0})
    for i, t in enumerate(task.targets):
        time.sleep(delay)
        sub = render_template(
            task.subject, t, ref_key=task.task_id, base_url=task.base_url)
        msg = render_template(
            task.html, t, ref_key=task.task_id, base_url=task.base_url)
        if send_email(t.email, sub, msg, task.sender, task.attachments, smtp):
            task.sent += 1
            await update_status(
                {'task_id': task.task_id, 'status': task.status, 'sent': task.sent, 'to_email': t.email})
        else:
            task.status = Status.FAIL
            await update_status(
                {'task_id': task.task_id, 'status': task.status, 'fail_at': i})
            break
    if task.sent == len(task.targets):
        task.status = Status.COMPLETE
    await update_status(
        {'task_id': task.task_id, 'status': task.status, 'sent': task.sent})


def task_warpper(task: TaskModel, smtp: SMTP):
    asyncio.run(send_email_task(task, smtp))


async def create_and_start_task(task: TaskModel, smtp: SMTP):
    try:
        t = threading.Thread(target=task_warpper, args=(task, smtp))
        t.start()
        return t.is_alive()
    except Exception as e:
        print(e)
    return False
