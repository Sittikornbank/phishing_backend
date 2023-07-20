
from datetime import datetime
from sqlalchemy.orm import Session
import uvicorn
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models import (Base, engine, get_db, get_group_by_id, create_group)
import os
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from schemas import Role, AuthContext
import schemas
import models
from auth import auth_permission, auth_token

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


@app.get("/groups", response_model=schemas.GroupListModel)
async def get_group_configss(page: int | None = 1, limit: int | None = 25, auth: AuthContext = Depends(auth_token)):
    # if empty in database --> Show {"count": 1,page": 1,"last_page": 2,"limit": 1,"smtp": []}
    auth_permission(auth=auth, roles=(Role.SUPER, Role.ADMIN))
    if auth.role == Role.SUPER:
        pass
    return models.get_all_group(page=page, size=limit)


@app.get("/groups/{id}", response_model=schemas.GroupDisplayModel)
async def get_group_config(id: int):
    group_config = get_group_by_id(id)
    if not group_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found")
    return group_config


@app.post("/groups", response_model=schemas.GroupDisplayModel)
async def create_group_config(temp_in: schemas.GroupDisplayModel):
    temp_in.modified_date = datetime.now()
    gs = models.create_group(temp_in)
    if gs:
        return gs
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid group format"
    )


# @app.put('/groups/{id}', response_model=schemas.GroupDisplayModel)
# async def modify_group(id: int, temp_in: schemas.GroupFormModel):


@app.delete('/groups/{id}')
async def del_group(id: int):
    temp = models.delete_group(id)
    if temp:
        return {'success': True}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )

###################################################


@app.get("/campaign", response_model=schemas.CampaignListModel)
async def get_smtp_configss(page: int | None = 1, limit: int | None = 25):
    smtp_data = models.get_campaign()
    if not smtp_data:
        return schemas.CampaignListModel()
# if empty in database --> Show {"count": 1,page": 1,"last_page": 2,"limit": 1,"smtp": []}
    return models.get_all_campaign(page=page, size=limit)


@app.get("/campaign/{userid}", response_model=schemas.CampaignDisplayModel)
async def get_smtp_config(userid: int):
    smtp_config = models.get_campaign_by_id(userid)
    if not smtp_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="campaign not found")
    return smtp_config


@app.post("/campaign")
async def create_smtp_config(s: schemas.CampaignModel):
    form_smtp = schemas.CampaignDisplayModel(user_id=s.user_id,
                                             name=s.name,
                                             templates_id=s.templates_id,
                                             status=s.status,
                                             url=s.url,
                                             smtp_id=s.smtp_id)
    s = models.create_campaign(form_smtp)
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
        detail="invalid format")


@app.delete("/campaign/{userid}")
async def delete_smtp_config(userid: int, db: Session = Depends(get_db)):
    existing_smtp = models.get_campaign_by_id(userid)
    if not existing_smtp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="campaign not found")
    models.delete_campaign(db, userid)
    return {"message": "campaign deleted"}


if __name__ == "__main__":
    models.init_org_db()
    uvicorn.run(app, host=os.getenv('HOST'), port=int(os.getenv('PORT')))
