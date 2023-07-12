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
# @app.get('/smtp')
# @app.get('/smtp/{userid}')


# @app.post('/smtp}')
# @app.put('/smtp/{userid}')


# @app.delete('/smtp/{userid}')
# @app.get('/smtp/{userid}/check')


# @app.get('/imap/')
# @app.get('/imap/{userid}')


# @app.post('/imap')
# @app.put('/imap/{userid}')
# @app.delete('/imap/{userid}')
# @app.get('/imap/{userid}')
# @app.get('/imap/{userid}/check')

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


# @app.get('/smtp')
# async def get_smtp_configs():
#     smtp_configs = get_smtp()
#     if not smtp_configs:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="smtp not found")

#     return smtp_configs

# @app.get("/smtp", response_model=SMTPListModel)
# async def get_smtp_configss(page: int = None, limit: int = None):

#     smtp_data = get_smtp()
#     if not smtp_data:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="smtp not found")

#     if page and page < 0:
#         page = 1
#     if limit and limit < 1:
#         limit = 25
#     smtp_configs = get_all_smtp(page, limit)

#     if smtp_configs and 'smtp' in smtp_configs:
#         return SMTPListModel(
#             count=smtp_configs['count'],
#             page=smtp_configs['page'],
#             last_page=(smtp_configs['count'] // smtp_configs['limit']) + 1,
#             limit=smtp_configs['limit'],
#             smtp=smtp_configs['smtp']
#         )

@app.get("/smtp", response_model=SMTPListModel)
async def get_smtp_configss(page: int = None, limit: int = None):

    smtp_data = get_smtp()
    if not smtp_data:
        return SMTPListModel()

    if page and page < 0:
        page = 1
    if limit and limit < 1:
        limit = 25
# if empty in database --> Show {"count": 1,page": 1,"last_page": 2,"limit": 1,"smtp": []}
    smtp_configs = get_all_smtp(page, limit)
    if smtp_configs and 'smtp' in smtp_configs:  # show get_all_smtp
        return SMTPListModel(
            count=smtp_configs['count'],
            page=smtp_configs['page'],
            last_page=(smtp_configs['count'] // smtp_configs['limit']) + 1,
            limit=smtp_configs['limit'],
            smtp=smtp_configs['smtp']
        )


# async def get_smtp_configs(page: int = None, limit: int = None):
#     if page and page < 0:
#         page = 1
#     if limit and limit < 1:
#         limit = 25

#     # Assuming this function retrieves all users
#     user = get_all_smtp(page, limit)

#     if user and 'smtp' in user:
#         return SMTPListModel(
#             count=user['count'],
#             page=user['page'],
#             last_page=(user['count'] // user['limit']) + 1,
#             limit=user['limit'],
#             smtp=user['smtp']
#         )
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail="SMTP not found")

    # if page and page < 0:
    #     page = 1
    # if limit and limit < 1:
    #     limit = 25
    # send = None
    # smtp_configs = get_all_smtp()
    # if not smtp_configs:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail="SMTP not found")
    # if send and 'smtp' in send:
    #     return IMAPListModel(count=send['count'], page=send['page'],
    #                          last_page=(send['count']//send['limit'])+1,
    #                          limit=send['limit'],
    #                          smtp=send['smtp'])
    # return IMAPListModel()


@app.get("/smtp/{userid}", response_model=SMTPDisplayModel)
async def get_smtp_config(userid: int):
    smtp_config = get_smtp_id(userid)
    if not smtp_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP not found")
    return smtp_config


@app.post("/smtp")
async def create_smtp_config(s: SMTPModel):
    form_smtp = SMTPDisplayModel(user_id=s.user_id,
                                 interface_type=s.interface_type,
                                 name=s.name,
                                 host=s.host,
                                 username=s.username,
                                 password=s.password,
                                 from_address=s.from_address,
                                 ignore_cert_errors=s.ignore_cert_errors)
    s = create_smtp(form_smtp)
    if s:
        return {
            'interface_type': s.interface_type,
            'name': s.name,
            'host': s.host,
            'username': s.username,
            'password': s.password,
            'from_address': s.from_address,
            'ignore_cert_errors': s.ignore_cert_errors
        }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="invalid smtp format")


@app.put("/smtp/{userid}", response_model=SMTPDisplayModel)
async def update_smtp_config(
    userid: int, smtp: SMTPFormModel, db: Session = Depends(get_db)
):
    existing_smtp = get_all_imap(userid)
    if not existing_smtp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP not found")
    updated_smtp = update_smtp(db, userid, smtp.dict(exclude_unset=True))
    return updated_smtp


@app.delete("/smtp/{userid}")
async def delete_smtp_config(userid: int, db: Session = Depends(get_db)):
    existing_smtp = get_smtp_id(userid)
    if not existing_smtp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP not found")
    delete_smtp(db, userid)
    return {"message": "SMTP deleted"}


# @app.get('/imap', response_model=IMAPListModel)
# async def get_imap_configs():
#     imap_configs = get_all_imap()
#     if not imap_configs:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="IMAP not found")

#     return imap_configs

@app.get("/imap", response_model=IMAPListModel)
async def get_imap_configss(page: int = None, limit: int = None):

    imap_data = get_imap()
    if not imap_data:
        return IMAPListModel()

    if page and page < 0:
        page = 1
    if limit and limit < 1:
        limit = 25
# if empty in database --> Show {"count": 1,page": 1,"last_page": 2,"limit": 1,"imap": []}
    imap_configs = get_all_imap(page, limit)
    if imap_configs and 'imap' in imap_configs:  # show get_all_smtp
        return IMAPListModel(
            count=imap_configs['count'],
            page=imap_configs['page'],
            last_page=(imap_configs['count'] // imap_configs['limit']) + 1,
            limit=imap_configs['limit'],
            imap=imap_configs['imap']
        )


@app.get('/imap/{userid}', response_model=IMAPDisplayModel)
async def get_imap_config(userid: int):
    imap_config = get_imap_id(userid)
    if not imap_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IMAP not found")
    return imap_config


@app.post('/imap')
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
    # i = create_imap(form_imap)
    # if i:
    #     return {
    #         'interface_type': i.interface_type,
    #         'name': i.name,
    #         'host': i.host,
    #         'username': i.username,
    #         'password': i.password,
    #         'from_address': i.from_address,
    #         'ignore_cert_errors': i.ignore_cert_errors
    #     }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid IMAP format")


@app.put('/imap/{userid}', response_model=IMAPDisplayModel)
async def update_imap_config(
        userid: int, imap: IMAPFormModel, db: Session = Depends(get_db)):
    existing_imap = get_imap_id(userid)
    if not existing_imap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IMAP not found")
    updated_imap = update_imap(db, userid, imap.dict(exclude_unset=True))
    return updated_imap


@app.delete('/imap/{userid}')
async def delete_imap_config(userid: int, db: Session = Depends(get_db)):
    existing_imap = get_imap_id(userid)
    if not existing_imap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="IMAP not found")
    delete_imap(db, userid)
    return {"message": "IMAP deleted"}


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
            user_id=1,
            interface_type="smtp",
            name="My SMTP Server",
            host="smtp.example.com",
            username="my_username",
            password="my_password",
            from_address="noreply@example.com",
            ignore_cert_errors=1
        ))

    uvicorn.run(app, host=os.getenv('HOST'), port=os.getenv('PORT'))
