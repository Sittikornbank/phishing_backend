import uvicorn
from fastapi import Request, FastAPI
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from schemas import (SMTPDisplayModel, SMTPFormModel,
                     SMTPModel, IMAPDisplayModel, IMAPFormModel,
                     IMAPModel, SMTPListModel, IMAPListModel, AuthContext, Role,
                     TaskModel)
from models import (Base, engine)
from dotenv import load_dotenv
from auth import auth_token, auth_permission
import os
import models
import tasks

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


@app.get("/smtp", response_model=SMTPListModel)
async def get_smtp_configs(
        page: int | None = 1, limit: int | None = 25, auth: AuthContext = Depends(auth_token)):
    if auth.role == Role.SUPER:
        return models.get_all_smtp(page=page, size=limit)
    elif auth.role == Role.AUDITOR or auth.role == Role.ADMIN:
        return models.get_smtps_by_org(id=auth.organization, page=page, size=limit, include_none=True)
    return models.get_smtps_by_user(id=auth.id, page=page, size=limit, include_none=True)


@app.get("/smtp/{id}", response_model=SMTPDisplayModel)
async def get_smtp_config(id: int, auth: AuthContext = Depends(auth_token)):
    smtp_config = models.get_smtp_id(id)
    if not smtp_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP not found")
    if auth.role == Role.SUPER:
        return smtp_config
    elif auth.role == Role.AUDITOR or auth.role == Role.ADMIN:
        if smtp_config.org_id != None and smtp_config.org_id != auth.organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SMTP not found")
        return smtp_config
    elif smtp_config.org_id != None or (
            smtp_config.user_id != None and smtp_config.user_id != auth.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP not found")
    return smtp_config


@app.post("/smtp", response_model=SMTPDisplayModel)
async def create_smtp_config(smtp: SMTPModel, auth: AuthContext = Depends(auth_token)):
    smtp.modified_date = datetime.now()
    smtp.interface_type = 'smtp'
    if auth.role == Role.SUPER:
        smtp = models.create_smtp(smtp)
        if smtp:
            return smtp
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid smtp format")

    smtp.user_id = auth.id
    smtp.org_id = None
    if auth.role == Role.ADMIN:
        smtp.org_id = auth.organization
    elif auth.role == Role.AUDITOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED")
    elif auth.role == Role.PAID:
        if models.count_smtp_by_user(auth.id) >= 3:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="already at maximum number of sending profiles")
    elif auth.role == Role.GUEST:
        if models.count_smtp_by_user(auth.id) >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="already at maximum number of sending profiles")
    smtp = models.create_smtp(smtp)
    if smtp:
        return smtp
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="invalid smtp format")


@app.put("/smtp/{id}", response_model=SMTPDisplayModel)
async def update_smtp_config(
        id: int, smtp: SMTPFormModel, auth: AuthContext = Depends(auth_token)):
    auth_permission(auth, roles=(
        Role.ADMIN, Role.SUPER, Role.GUEST, Role.PAID))
    if auth.role == Role.SUPER:
        s = models.update_smtp(id, smtp.dict(exclude_unset=True))
        if s:
            return s
    elif auth.role == Role.ADMIN:
        s = models.get_smtp_id(id)
        if s and s.org_id == auth.organization:
            s = models.update_smtp(id, smtp.dict(exclude_unset=True))
            if s:
                return s
    elif auth.role == Role.GUEST or auth.role == Role.PAID:
        s = models.get_smtp_id(id)
        if s and s.user_id == auth.id:
            s = models.update_smtp(id, smtp.dict(exclude_unset=True))
            if s:
                return s

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="SMTP not found")


@app.delete("/smtp/{id}")
async def delete_smtp_config(id: int, auth: AuthContext = Depends(auth_token)):
    auth_permission(auth, roles=(
        Role.ADMIN, Role.SUPER, Role.GUEST, Role.PAID))
    if auth.role == Role.SUPER:
        s = models.delete_smtp(id)
        if s:
            return {'success': s}
    elif auth.role == Role.ADMIN:
        s = models.get_smtp_id(id)
        if s and s.org_id == auth.organization:
            s = models.delete_smtp(id)
            if s:
                return {'success': s}
    elif auth.role == Role.GUEST or auth.role == Role.PAID:
        s = models.get_smtp_id(id)
        if s and s.user_id == auth.id:
            s = models.delete_smtp(id)
            if s:
                return {'success': s}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="SMTP not found")


@app.get('/smtp/{id}/check')
async def test_smtp(id: int, auth: AuthContext = Depends(auth_token)):
    auth_permission(auth, roles=(
        Role.ADMIN, Role.SUPER, Role.GUEST, Role.PAID))
    s = models.get_smtp_id(id)
    if not s:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP not found")
    if auth.role == Role.SUPER:
        result = tasks.send_test_email(s)
        return {'success': result}
    elif auth.role == Role.ADMIN:
        if s and s.org_id == auth.organization:
            result = tasks.send_test_email(s)
            return {'success': result}
    elif auth.role == Role.GUEST or auth.role == Role.PAID:
        if s and s.user_id == auth.id:
            result = tasks.send_test_email(s)
            return {'success': result}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="SMTP not found")


@app.get('/check/smtp')
async def test_smtp(smtp: SMTPModel, auth: AuthContext = Depends(auth_token)):
    auth_permission(auth, roles=(
        Role.ADMIN, Role.SUPER, Role.GUEST, Role.PAID))
    result = tasks.send_test_email(smtp)
    return {'success': result}


@app.get("/imap", response_model=IMAPListModel)
async def get_imap_configss(
        page: int | None = 1, limit: int | None = 25, auth: AuthContext = Depends(auth_token)):

    return models.get_all_imap(page=page, size=limit)


@app.get('/imap/{id}', response_model=IMAPDisplayModel)
async def get_imap_config(id: int, auth: AuthContext = Depends(auth_token)):
    imap_config = models.get_imap_id(id)
    if not imap_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IMAP not found")
    return imap_config


@app.post('/imap', response_model=IMAPModel)
async def create_imap_config(imap: IMAPModel, auth: AuthContext = Depends(auth_token)):
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
    created_imap = models.create_imap(form_imap)
    if created_imap:
        return created_imap
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid IMAP format")


@app.put('/imap/{id}', response_model=IMAPDisplayModel)
async def update_imap_config(
        id: int, imap: IMAPFormModel, auth: AuthContext = Depends(auth_token)):
    updated_imap = models.update_imap(id, imap.dict(exclude_unset=True))
    if updated_imap:
        return updated_imap
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="IMAP not found")


@app.delete('/imap/{id}')
async def delete_imap_config(id: int, auth: AuthContext = Depends(auth_token)):
    c = models.delete_imap(id)
    if c:
        return {"success": c}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="IMAP not found")


@app.get('/imap/{id}/check')
async def check_imap_config(id: int, auth: AuthContext = Depends(auth_token)):
    imap_config = models.get_imap_id(id)
    if not imap_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="IMAP not found")
    # Perform the necessary checks on the IMAP configuration
    # Implement the logic to check IMAP configuration, e.g., connecting to the IMAP server
    # Return appropriate response based on the checks
    return {"message": "IMAP configuration is valid"}


@app.post("/mails")
async def create_and_start_task(task: TaskModel):
    smtp = models.get_smtp_id(task.smtp_id)
    if not smtp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP Not Found")
    res = await tasks.create_and_start_task(task, smtp)
    return {'success': res}

if __name__ == "__main__":
    # Check if SMTP configuration with user_id=1 already exists
    existing_smtp = models.get_smtp_id(1)
    if not existing_smtp:
        models.create_smtp(SMTPDisplayModel(
            user_id=None,
            org_id=None,
            interface_type="smtp",
            name=os.getenv('DEV_NAME'),
            host=os.getenv('DEV_HOST'),
            username=os.getenv('DEV_USERNAME'),
            password=os.getenv('DEV_PASSWORD'),
            from_address="noreply@example.com",
            ignore_cert_errors=True
        ))

    uvicorn.run(app, host=os.getenv('HOST'), port=int(os.getenv('PORT')))
