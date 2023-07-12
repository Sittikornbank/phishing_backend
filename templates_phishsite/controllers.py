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


@app.post('/templates')
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


@app.put('/templates/{temp_id}')
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


@app.post('/site_templates')
async def add_site_template(temp_in: schemas.SiteModel,
                            token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp_in.create_at = datetime.now()
    temp = models.create_site_template(temp=temp_in)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Parameter Error"
    )


@app.put('/site_templates/{temp_id}')
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
    temp = models.delete_site_temp(temp_id)
    if temp:
        return {'success': temp}
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


@app.post('/email_templates')
async def add_email_template(temp_in: schemas.EmailModel,
                             token: str = Depends(get_token)):
    await check_permission(token, (Role.SUPER,))
    temp_in.create_at = datetime.now()
    temp = models.create_email_template(temp=temp_in)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Parameter Error"
    )


@app.put('/email_templates/{temp_id}')
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
    temp = models.delete_email_temp(temp_id)
    if temp:
        return {'success': temp}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv('HOST'), port=os.getenv('PORT'))
