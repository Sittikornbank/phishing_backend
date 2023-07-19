import base64
import uvicorn
from datetime import datetime
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from auth import get_token, check_permission, check_token, protect_api, auth_token, auth_permission
from schemas import Role, Visible, AuthContext
import os
import schemas
import models
import workers
from random import choices

import base64

load_dotenv()
models.Base.metadata.create_all(bind=models.engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory=os.path.dirname(
    os.path.realpath(__file__))+"/images"), name="images")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    detail = ""
    try:
        # detail = str(exc.errors())
        detail = exc.errors()[0]['loc'][-1]+','+exc.errors()[0]['msg']
    except Exception as e:
        print(e)
        detail = str(exc.errors())
    return JSONResponse({'detail': detail},
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get('/templates', response_model=schemas.TemplateListModel)
async def get_templates(page: int | None = 1, limit: int | None = 25, auth: AuthContext = Depends(auth_token)):
    return models.get_all_templates(page=page, size=limit)


@app.get('/templates/{temp_id}', response_model=schemas.TemplateDisplayModel)
async def get_template(temp_id: int, auth: AuthContext = Depends(auth_token)):

    temp = models.get_template_by_id(temp_id)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.post('/templates', response_model=schemas.TemplateModel)
async def add_template(temp_in: schemas.TemplateModel,
                       auth: AuthContext = Depends(auth_token)):
    auth_permission(auth=auth, roles=(Role.SUPER))
    temp_in.create_at = datetime.now()
    temp = models.create_template(temp_in)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Parameter Error"
    )


@app.put('/templates/{temp_id}', response_model=schemas.TemplateModel)
async def modify_template(temp_id: int, temp_in: schemas.TemplateFromModel,
                          token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    t = dict()
    t['modified_date'] = datetime.now()
    if temp_in.name:
        t['name'] = temp_in.name
    if temp_in.visible:
        t['visible'] = temp_in.visible
    if temp_in.owner_id:
        t['owner_id'] = temp_in.owner_id
    if temp_in.org_id:
        t['temp_in.org_id'] = temp_in.org_id
    if temp_in.description:
        t['description'] = temp_in.description
    if temp_in.site_template:
        t['site_template'] = temp_in.site_template
    if temp_in.mail_template:
        t['mail_template'] = temp_in.mail_template
    temp = models.update_template(t, temp_id)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.delete('/templates/{temp_id}')
async def del_template(temp_id: int, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp = models.delete_template(temp_id)
    if temp:
        return {'success': temp}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.get('/site_templates', response_model=schemas.SiteListModel)
async def get_site_templates(page: int | None = 1, limit: int | None = 25,
                             token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    return models.get_all_site_templates(page=page, size=limit)


@app.get('/site_templates/{temp_id}', response_model=schemas.SiteModel)
async def get_site_template(temp_id: int, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp = models.get_site_template_by_id(id=temp_id)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


IMAGES_FOLDER = "templates_phishsite/images"


@app.post('/site_templates', response_model=schemas.SiteModel)
async def add_site_template(temp_in: schemas.SiteModel, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp_in.create_at = datetime.now()
    temp_in = validate_and_set_image(temp_in)
    temp = models.create_site_template(temp=temp_in)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Parameter Error"
    )


@app.put('/site_templates/{temp_id}', response_model=schemas.SiteModel)
async def modify_site_template(temp_id: int, temp_in: schemas.SiteFormModel,
                               token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    t = dict()
    if temp_in.name:
        t['name'] = temp_in.name
    if temp_in.visible:
        t['visible'] = temp_in.visible
    if temp_in.owner_id != None:
        t['owner_id'] = temp_in.owner_id
    if temp_in.org_id != None:
        t['temp_in.org_id'] = temp_in.org_id
    if temp_in.html != None:
        t['html'] = temp_in.html
    if temp_in.capture_credentials != None:
        t['capture_credentials'] = temp_in.capture_credentials
    if temp_in.capture_passwords != None:
        t['capture_passwords'] = temp_in.capture_passwords
    if temp_in.redirect_url != None:
        t['redirect_url'] = temp_in.redirect_url
    if temp_in.image_site != None:
        temp_in = validate_and_set_image(temp_in)
        t['image_site'] = temp_in.image_site
    temp = models.update_site_temp(id=temp_id, temp_in=t)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.delete('/site_templates/{temp_id}')
async def del_site_template(temp_id: int, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp = models.get_site_template_by_id(temp_id)
    if temp:
        if temp.image_site:
            image_path = os.path.join(IMAGES_FOLDER, temp.image_site)
            if os.path.exists(image_path):
                os.remove(image_path)

        models.delete_site_temp(temp_id)
        return {'success': True}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.get('/email_templates', response_model=schemas.EmailListModel)
async def get_email_templates(page: int | None = 1, limit: int | None = 25,
                              token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    return models.get_all_email_templates(page=page, size=limit)


@app.get('/email_templates/{temp_id}', response_model=schemas.EmailModel)
async def get_email_template(temp_id: int, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp = models.get_email_template_by_id(id=temp_id)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.post('/email_templates', response_model=schemas.EmailModel)
async def add_email_template(temp_in: schemas.EmailModel,
                             token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp_in.create_at = datetime.now()
    temp_in = validate_and_set_image(temp_in)
    temp = models.create_email_template(temp=temp_in)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Parameter Error"
    )


@app.put('/email_templates/{temp_id}', response_model=schemas.EmailModel)
async def modify_email_template(temp_id: int, temp_in: schemas.EmailFormModel,
                                token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    t = dict()
    if temp_in.name:
        t['name'] = temp_in.name
    if temp_in.visible:
        t['visible'] = temp_in.visible
    if temp_in.owner_id != None:
        t['owner_id'] = temp_in.owner_id
    if temp_in.org_id != None:
        t['temp_in.org_id'] = temp_in.org_id
    if temp_in.html != None:
        t['html'] = temp_in.html
    if temp_in.envelope_sender != None:
        t['envelope_sender'] = temp_in.envelope_sender
    if temp_in.subject != None:
        t['subject'] = temp_in.subject
    if temp_in.attachments != None:
        t['attachments'] = temp_in.attachments
    if temp_in.image_email != None:
        temp_in = validate_and_set_image(temp_in)
        t['image_email'] = temp_in.image_email
    temp = models.update_email_temp(id=temp_id, temp_in=t)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.delete('/email_templates/{temp_id}')
async def del_email_template(temp_id: int, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp = models.get_email_template_by_id(temp_id)
    if temp:
        if temp.image_email:
            image_path = os.path.join(IMAGES_FOLDER, temp.image_email)
            if os.path.exists(image_path):
                os.remove(image_path)

        models.delete_email_temp(temp_id)
        return {'success': True}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.get('/phishsites', response_model=schemas.PhishsiteListModel)
async def get_phishsites(page: int | None = 1, limit: int | None = 25,
                         token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    return models.get_all_phishsites(page=page, size=limit)


@app.get('/phishsites/{temp_id}', response_model=schemas.PhishsiteModel)
async def get_phishsite(temp_id: int, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp = models.get_phishsite_by_id(id=temp_id)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.post('/phishsites', response_model=schemas.PhishsiteModel)
async def add_phishsite(temp_in: schemas.PhishsiteModel,
                        token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp = models.create_phishsite(temp_in=temp_in)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Parameter Error"
    )


@app.put('/phishsites/{temp_id}', response_model=schemas.PhishsiteModel)
async def modify_phishsite(temp_id: int, temp_in: schemas.PhishsiteFromModel,
                           token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    t = dict()
    if temp_in.name:
        t['name'] = temp_in.name
    if temp_in.uri:
        t['uri'] = temp_in.uri
    if temp_in.secret_key:
        t['secret_key'] = temp_in.secret_key

    temp = models.update_phishsite(temp_in=t, id=temp_id)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.delete('/phishsites/{temp_id}')
async def del_phishsite(temp_id: int, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp = models.delete_phishsite(id=temp_id)
    if temp:
        return {'success': temp}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.get('/phishsites/{temp_id}/check')
async def check_phishsite(temp_id: int, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    return await workers.ping_worker_by_id(temp_id)


@app.get('/workers/code')
async def check_phishsite(lang: str, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    return workers.code(lang)


@app.post('/workers')
async def handle_worker_post(req: Request, token: str = Depends(get_token)):
    body = await req.json()
    if body and 'ref_key' in body and 'ref_id' in body and 'event_type' in body:
        wid = workers.validate_token(token)
        if wid < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not Found"
            )
        context = schemas.EventContext(ref_key=body['ref_key'],
                                       ref_id=body['ref_id'],
                                       event_type=body['event_type'])
        if 'payload' in body and body['payload']:
            context.payload = body['payload']
        workers.process_event(context, wid)
        if body['event_type'] == schemas.Event.CLICK:
            temp = workers.get_landing(context, wid)
            if temp:
                return {'html': temp.html}
        elif body['event_type'] == schemas.Event.SUBMIT:
            temp = workers.get_landing(context, wid)
            if temp:
                return {'redirect_url': temp.redirect_url}
        else:
            return {'success': workers.get_dotpng(context, wid)}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.get('/landing', response_model=list[schemas.Task])
def get_all_tasks(auth: AuthContext = Depends(auth_token)):
    auth_permission(auth=auth, roles=(Role.SUPER,))
    return workers.get_all_tasks()


@app.post('/landing', response_model=schemas.EmailResSchema)
def start_landing_campaign(c: schemas.LaunchingModel, _=Depends(protect_api)):
    template: schemas.TemplateModel = models.get_template_by_id(
        c.req.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template Not Found"
        )
    if c.auth.role == Role.AUDITOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED"
        )
    if template.visible == Visible.NONE and c.auth.role != Role.SUPER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED"
        )
    if template.visible == Visible.PAID and c.auth.role == Role.GUEST:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED"
        )
    if template.visible == Visible.CUSTOM:
        if c.auth.role == Role.ADMIN and template.org_id != c.auth.organization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="UNAUTHORIZED"
            )
        if (c.auth.role in [Role.PAID, Role.GUEST]) and template.owner_id != c.auth.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="UNAUTHORIZED"
            )
    if not (template.site_template and template.mail_template):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Template Not Complete"
        )
    site = models.get_site_template_by_id(template.site_template)
    mail = models.get_email_template_by_id(template.mail_template)
    if not (site and mail and site.phishsite_id):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Template Not Complete, Some resounce may not existed"
        )
    if not workers.add_landing_task(req=c.req, site=site, auth=c.auth):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Landing Task with ref_key already existed."
        )
    setattr(mail, "base_url", site.phishsite_id)
    return mail


@app.delete('/landing')
def remove_landing_campaign(ref_key: str, auth: AuthContext, _=Depends(protect_api)):
    task = workers.get_task_by_ref(ref_key)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    if auth.role == Role.AUDITOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot Access Landing"
        )
    if auth.role in [Role.PAID, Role.GUEST] and auth.id != task.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot Access Landing"
        )
    if auth.role == Role.ADMIN and auth.organization != task.org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot Access Landing"
        )
    workers.remove_task(ref_key)
    return {'success': True}


def validate_and_set_image(temp_in:
                           schemas.SiteModel | schemas.EmailModel |
                           schemas.SiteFormModel | schemas.EmailFormModel):
    if hasattr(temp_in, 'image_site'):
        b64 = temp_in.image_site
    elif hasattr(temp_in, 'image_email'):
        b64 = temp_in.image_email
    try:
        h, b64 = b64.split(',')
        if h != 'data:image/png;base64':
            raise Exception()
        # Check if b64 is base64-encoded
        base64.b64decode(b64.encode())

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 encoding or format --> data:image/png;base64"
        )

    iname = ''.join(choices('abcdefghijklmnopqrstuvwxyz', k=8))
    image_filename = iname + '.png'
    image_path = os.path.join(IMAGES_FOLDER, image_filename)

    with open(image_path, "wb") as image_file:
        image_file.write(base64.b64decode(b64.encode()))
    if hasattr(temp_in, 'image_site'):
        temp_in.image_site = image_filename
    elif hasattr(temp_in, 'image_email'):
        temp_in.image_email = image_filename
    return temp_in


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv('HOST'), port=int(os.getenv('PORT')))
