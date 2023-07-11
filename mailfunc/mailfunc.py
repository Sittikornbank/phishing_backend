import uvicorn
from fastapi import Request, FastAPI
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
from schemas import (SMTPDisplayModel, SMTPFormModel, SMTPModel)
from models import (Base, engine, get_db, get_smtp, get_smtp_id,
                    create_smtp, update_smtp, delete_smtp)
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


@app.get("/smtp", response_model=list[SMTPDisplayModel])
async def get_smtp_configs():
    smtp_configs = get_smtp()
    if not smtp_configs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="SMTP not found")
    return smtp_configs


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
    existing_smtp = get_smtp_id(userid)
    if not existing_smtp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP not found",
        )
    updated_smtp = update_smtp(db, userid, smtp.dict(exclude_unset=True))
    return updated_smtp


@app.delete("/smtp/{userid}", response_model=SMTPDisplayModel)
async def delete_smtp_config(userid: int, db: Session = Depends(get_db)):
    existing_smtp = get_smtp_id(userid)
    if not existing_smtp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMTP not found",
        )
    delete_smtp(db, userid)
    return {"message": "SMTP deleted"}


if __name__ == "__main__":
    create_smtp(SMTPDisplayModel(user_id=1,
                                 interface_type="smtp",
                                 name="My SMTP Server",
                                 host="smtp.example.com",
                                 username="my_username",
                                 password="my_password",
                                 from_address="noreply@example.com",
                                 ignore_cert_errors=1
                                 ))
    uvicorn.run(app, host=os.getenv('HOST'), port=os.getenv('PORT'))
