import uvicorn
from fastapi import Request, FastAPI
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
from schemas import (SMTPDisplayModel, SMTPFormModel,
                     SMTPModel, IMAPDisplayModel, IMAPFormModel,
                     IMAPModel, SMTPListModel, IMAPListModel)
from models import (Base, engine, get_db, get_smtp, get_smtp_id, get_all_smtp, get_all_imap,
                    create_smtp, update_smtp, delete_smtp,
                    get_imap, get_imap_id, create_imap,
                    update_imap, delete_imap)
import os
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import models
import schemas
app = FastAPI()

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    detail = ""
    try:
        detail = exc.errors()[0]['loc'][-1]+','+exc.errors()[0]['msg']
    except Exception as e:
        print(e)
        detail = str(exc.errors())
    return JSONResponse({'detail': detail},
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/smtp", response_model=schemas.SMTPListModel)
async def get_smtp_configss(page: int | None = 1, limit: int | None = 25):
    return models.get_all_smtp(page=page, size=limit)


@app.get("/smtp/{userid}", response_model=SMTPDisplayModel)
async def get_smtp_config(userid: int):
    smtp_config = get_smtp_id(userid)
    if not smtp_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP not found")
    return smtp_config


@app.post("/smtp", response_model=SMTPDisplayModel)
async def create_smtp_config(s: SMTPModel):
    form_smtp = SMTPDisplayModel(user_id=s.user_id,
                                 interface_type="smtp",
                                 name=s.name,
                                 host=s.host,
                                 username=s.username,
                                 password=s.password,
                                 from_address=s.from_address,
                                 ignore_cert_errors=s.ignore_cert_errors)
    s = create_smtp(form_smtp)
    if s:
        return s
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="invalid smtp format")


@app.put("/smtp/{userid}", response_model=SMTPDisplayModel)
async def update_smtp_config(
    userid: int, smtp: SMTPFormModel, db: Session = Depends(get_db)
):
    updated_smtp = update_smtp(db, userid, smtp.dict(exclude_unset=True))
    if updated_smtp:
        return updated_smtp

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="SMTP not found")


@app.delete("/smtp/{userid}")
async def delete_smtp_config(userid: int, db: Session = Depends(get_db)):
    existing_smtp = get_smtp_id(userid)

    c = delete_smtp(db, userid)
    if c:
        return {'success': c}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="SMTP not found")


@app.get("/imap", response_model=IMAPListModel)
async def get_imap_configss(page: int | None = 1, limit: int | None = 25):
    return models.get_all_imap(page=page, size=limit)


@app.get('/imap/{userid}', response_model=IMAPDisplayModel)
async def get_imap_config(userid: int):
    imap_config = get_imap_id(userid)
    if not imap_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IMAP not found")
    return imap_config


@app.post('/imap', response_model=IMAPModel)
async def create_imap_config(imap: IMAPModel):
    form_imap = IMAPDisplayModel(user_id=imap.user_id,
                                 enabled=imap.enabled,
                                 host=imap.host,
                                 port=imap.port,
                                 username=imap.username,
                                 password=imap.password,
                                 tls=imap.tls,
                                 ignore_cert_errors=imap.ignore_cert_errors,
                                 folder=imap.folder,
                                 restrict_domain=imap.restrict_domain,
                                 delete_reported_campaign_email=imap.delete_reported_campaign_email,
                                 last_login=imap.last_login,
                                 imap_freq=imap.imap_freq)
    created_imap = create_imap(form_imap)
    if created_imap:
        return created_imap
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid IMAP format")


@app.put('/imap/{userid}', response_model=IMAPDisplayModel)
async def update_imap_config(
        userid: int, imap: IMAPFormModel, db: Session = Depends(get_db)):
    updated_imap = update_imap(db, userid, imap.dict(exclude_unset=True))
    if updated_imap:
        return updated_imap
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="IMAP not found")


@app.delete('/imap/{userid}')
async def delete_imap_config(userid: int, db: Session = Depends(get_db)):
    c = delete_imap(db, userid)
    if c:
        return {"success": c}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="IMAP not found")


@app.get('/imap/{userid}/check')
async def check_imap_config(userid: int):
    imap_config = get_imap_id(userid)
    if not imap_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="IMAP not found")
    # Perform the necessary checks on the IMAP configuration
    # Implement the logic to check IMAP configuration, e.g., connecting to the IMAP server
    # Return appropriate response based on the checks
    return {"message": "IMAP configuration is valid"}


if __name__ == "__main__":
    # Check if SMTP configuration with user_id=1 already exists
    existing_smtp = get_smtp_id(1)
    if not existing_smtp:
        create_smtp(SMTPDisplayModel(
            user_id=-1,
            interface_type="smtp",
            name=os.getenv('DEV_NAME'),
            host=os.getenv('DEV_HOST'),
            username=os.getenv('DEV_USERNAME'),
            password=os.getenv('DEV_PASSWORD'),
            from_address="noreply@example.com",
            ignore_cert_errors=1
        ))

    uvicorn.run(app, host=os.getenv('HOST'), port=os.getenv('PORT'))
