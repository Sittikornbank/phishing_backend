import uvicorn
from fastapi import Request, FastAPI
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
from schemas import (CampaignDisplayModel, CampaignFormModel,
                     CampaignListModel, CampaignModel)
from models import (Base, engine, get_db, get_all_campaigns,
                    get_campaign, get_campaign_by_id, create_campaign, delete_campaign, get_campaign_by_id)
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
        # detail = str(exc.errors())
        detail = exc.errors()[0]['loc'][-1]+','+exc.errors()[0]['msg']
    except Exception as e:
        print(e)
        detail = str(exc.errors())
    return JSONResponse({'detail': detail},
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/campaign", response_model=schemas.CampaignListModel)
async def get_smtp_configss(page: int | None = 1, limit: int | None = 25):
    smtp_data = get_campaign()
    if not smtp_data:
        return CampaignListModel()
# if empty in database --> Show {"count": 1,page": 1,"last_page": 2,"limit": 1,"smtp": []}
    return models.get_all_campaigns(page=page, size=limit)


@app.get("/campaign/{userid}", response_model=CampaignDisplayModel)
async def get_smtp_config(userid: int):
    smtp_config = get_campaign_by_id(userid)
    if not smtp_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="campaign not found")
    return smtp_config


@app.post("/campaign")
async def create_smtp_config(s: CampaignModel):
    form_smtp = CampaignDisplayModel(user_id=s.user_id,
                                     name=s.name,
                                     templates_id=s.templates_id,
                                     status=s.status,
                                     url=s.url,
                                     smtp_id=s.smtp_id)
    s = create_campaign(form_smtp)
    if s:
        return {
            'name': s.name,
            'templates_id': s.templates_id,
            'status': s.status,
            'url': s.url,
            'smtp_id': s.smtp_id
        }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="invalid smtp format")


@app.delete("/campaign/{userid}")
async def delete_smtp_config(userid: int, db: Session = Depends(get_db)):
    existing_smtp = get_campaign_by_id(userid)
    if not existing_smtp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="campaign not found")
    delete_campaign(db, userid)
    return {"message": "campaign deleted"}

if __name__ == "__main__":
    # Check if SMTP configuration with user_id=1 already exists
    # existing_smtp = get_smtp_id(1)
    # if not existing_smtp:
    #     create_smtp(SMTPDisplayModel(
    #         user_id=1,
    #         interface_type="smtp",
    #         name="My SMTP Server",
    #         host="smtp.example.com",
    #         username="my_username",
    #         password="my_password",
    #         from_address="noreply@example.com",
    #         ignore_cert_errors=1
    #     ))

    uvicorn.run(app, host=os.getenv('HOST'), port=os.getenv('PORT'))
