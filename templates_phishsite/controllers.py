import base64
import uvicorn
from datetime import datetime
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from auth import get_token, check_permission
from schemas import Role
import os
import schemas
import models
<<<<<<< HEAD
import workers
=======
from random import choices
>>>>>>> 87c15e0b53387e0d55d50166e58aad96c95af48a

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
def get_templates(page: int | None = 1, limit: int | None = 25, token: str = Depends(get_token)):
    return models.get_all_templates(page=page, size=limit)


@app.get('/templates/{temp_id}', response_model=schemas.TemplateDisplayModel)
def get_template(temp_id: int, token: str = Depends(get_token)):
    temp = models.get_template_by_id(temp_id)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


@app.post('/templates', response_model=schemas.TemplateModel)
async def add_template(temp_in: schemas.TemplateModel,
                       token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
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


<<<<<<< HEAD
@app.get('/phishsites/{temp_id}/check')
async def check_phishsite(temp_id: int, token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    return workers.ping_worker_by_id(temp_id)


@app.get('/phishsites/code')
async def check_phishsite(token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    pass


@app.get('/workers')
async def handle_worker_get(req: Request):
    body = await req.json()


@app.post('/workers')
async def handle_worker_post(req: Request):
    body = await req.json()

=======
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
            detail="Invalid base64 encoding or "
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


>>>>>>> 87c15e0b53387e0d55d50166e58aad96c95af48a
if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv('HOST'), port=os.getenv('PORT'))
