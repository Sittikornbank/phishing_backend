
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
from schemas import Role, AuthContext, GroupFormModel
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

# --------------------------------- Groups ---------------------------------#


@app.get("/groups", response_model=schemas.GroupListModel)
async def get_group_configss(page: int | None = 1, limit: int | None = 25, auth: AuthContext = Depends(auth_token)):
    if auth.role == Role.SUPER:
        return models.get_all_group(page, limit)
    elif auth.role == Role.AUDITOR or auth.role == Role.ADMIN:
        return models.get_group_by_org(auth.organization, page, limit)
    # read main database
    return models.get_group_by_user(id=auth.id, page=page, size=limit, include_none=True)


@app.get("/groups/{id}", response_model=schemas.GroupDisplayModel)
async def get_group_config(id: int, auth: AuthContext = Depends(auth_token)):
    group = get_group_by_id(id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not Found group of id :{id}")
    if auth.role == Role.SUPER:
        return group
    elif auth.role == Role.AUDITOR or auth.role == Role.ADMIN:
        if group.org_id != None and group.org_id != auth.organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Not Found group of id :{id}")
        return group
    elif group.org_id != None or (
            group.user_id != None and group.user_id != auth.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not Found group of id :{id}")
    return group


# @app.get("/groups/summary")
# # async def get_summary(id: int, auth: AuthContext = Depends(auth_token)):
#     auth_permission(auth=auth, roles=(Role.SUPER, Role.ADMIN, Role.AUDITOR))
#     if auth.role == Role.SUPER:

# @app.get("/groups/summary/{id}")
# # async def get_summary_by_id(id: int, auth: AuthContext = Depends(auth_token)):
#     auth_permission(auth=auth, roles=(Role.SUPER, Role.ADMIN, Role.AUDITOR))
#     if auth.role == Role.SUPER:


@app.post("/groups", response_model=schemas.GroupDisplayModel)
async def create_group_config(group: schemas.GroupModel, auth: AuthContext = Depends(auth_token)):
    group.modified_date = datetime.now()
    if auth.role == Role.SUPER:
        group = models.create_group(group)
        if group:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            return group
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid group format")
    group.user_id = auth.id
    group.org_id = None
    if auth.role == Role.ADMIN:
        group.org_id = auth.organization
    elif auth.role == Role.AUDITOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED")
    elif auth.role == Role.PAID:
        if models.count_group_by_user(auth.id) >= 10:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="already at maximum number of create Group")
    elif auth.role == Role.GUEST:
        if models.count_group_by_user(auth.id) >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="already at maximum number of create Group")
    group = models.create_group(group)
    if group:
        return group
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="invalid group format")


@app.put("/groups/{id}", response_model=models.GroupDisplayModel)
async def update_smtp_config(id: int, group: GroupFormModel, auth: AuthContext = Depends(auth_token)):
    auth_permission(auth, roles=(
        Role.ADMIN, Role.SUPER, Role.GUEST, Role.PAID))
    if auth.role == Role.SUPER:
        s = models.update_group(id, group.dict(exclude_unset=True))
        if s:
            return s
    elif auth.role == Role.ADMIN:
        s = models.get_group_by_id(id)
        if s and s.org_id == auth.organization:
            s = models.update_group(id, group.dict(exclude_unset=True))
            if s:
                return s
    elif auth.role == Role.GUEST or auth.role == Role.PAID:
        s = models.get_group_by_id(id)
        if s and s.user_id == auth.id:
            s = models.update_group(id, group.dict(exclude_unset=True))
            if s:
                return s
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Group not found")

# @app.put('/groups/{id}', response_model=schemas.GroupDisplayModel)
# async def modify_group(id: int, temp_in: schemas.GroupFormModel):


@app.delete("/groups/{id}")
async def delete_smtp_config(id: int, auth: AuthContext = Depends(auth_token)):
    auth_permission(auth, roles=(
        Role.ADMIN, Role.SUPER, Role.GUEST, Role.PAID))
    if auth.role == Role.SUPER:
        group = models.delete_group(id)
        if group:
            return {'success': True}
    elif auth.role == Role.ADMIN:
        group = models.get_group_by_id(id)
        if group and group.org_id == auth.organization:
            group = models.delete_group(id)
            if group:
                return {'success': True}
    elif auth.role == Role.GUEST or auth.role == Role.PAID:
        group = models.get_group_by_id(id)
        if group and group.user_id == auth.id:
            group = models.delete_group(id)
            if group:
                return {'success': True}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Group not found")


# @app.post("/groups/import")
# async def import_group(auth: AuthContext = Depends(auth_token)):
#     auth_permission(auth=auth, roles=(Role.SUPER, Role.ADMIN, Role.AUDITOR))
#     if auth.role == Role.SUPER:

# --------------------------------  Campaigns --------------------------------#


@app.get("/campaigns", response_model=schemas.CampaignListModel)
async def get_campaign_configss(page: int | None = 1, limit: int | None = 25, auth: AuthContext = Depends(auth_token)):
    if auth.role == Role.SUPER:
        return models.get_all_campaign(page, limit)
    elif auth.role == Role.AUDITOR or auth.role == Role.ADMIN:
        return models.get_campaign_by_org(auth.organization, page, limit)
    # read main database
    return models.get_campaign_by_user(id=auth.id, page=page, size=limit, include_none=True)


# async def get_campaign_configss(page: int | None = 1, limit: int | None = 25):
#     smtp_data = models.get_campaign()
#     if not smtp_data:
#         return schemas.CampaignListModel()
# # if empty in database --> Show {"count": 1,page": 1,"last_page": 2,"limit": 1,"smtp": []}
#     return models.get_all_campaign(page=page, size=limit)


@app.get("/campaigns/{id}", response_model=schemas.CampaignDisplayModel)
async def get_campaign_config(id: int, auth: AuthContext = Depends(auth_token)):
    campaign = models.get_campaign_by_id(id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not Found campaign of id :{id}")
    if auth.role == Role.SUPER:
        return campaign
    elif auth.role == Role.AUDITOR or auth.role == Role.ADMIN:
        if campaign.org_id != None and campaign.org_id != auth.organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Not Found campaign of id :{id}")
        return campaign
    elif campaign.org_id != None or (
            campaign.user_id != None and campaign.user_id != auth.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not Found campaign of id :{id}")
    return campaign


@app.post("/campaigns", response_model=schemas.CampaignDisplayModel)
async def create_campaign_config(campaign: schemas.CampaignModel, auth: AuthContext = Depends(auth_token)):
    campaign.create_date = datetime.now()
    if auth.role == Role.SUPER:
        campaign = models.create_campaign(campaign)
        if campaign:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            return campaign
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid campaign format")
    campaign.user_id = auth.id
    campaign.org_id = None
    if auth.role == Role.ADMIN:
        campaign.org_id = auth.organization
    elif auth.role == Role.AUDITOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED")
    elif auth.role == Role.PAID:
        if models.count_campaign_by_user(auth.id) >= 10:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="already at maximum number of sending profiles")
    elif auth.role == Role.GUEST:
        if models.count_campaign_by_user(auth.id) >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="already at maximum number of sending profiles")
    campaign = models.create_campaign(campaign)
    if campaign:
        return campaign
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="invalid campaign format")


@app.delete("/campaigns/{id}")
async def delete_campaign_config(id: int, auth: AuthContext = Depends(auth_token)):
    auth_permission(auth, roles=(
        Role.ADMIN, Role.SUPER, Role.GUEST, Role.PAID))
    if auth.role == Role.SUPER:
        campaign = models.delete_campaign(id)
        if campaign:
            return {'success': True}
    elif auth.role == Role.ADMIN:
        campaign = models.get_campaign_by_id(id)
        if campaign and campaign.org_id == auth.organization:
            campaign = models.delete_campaign(id)
            if campaign:
                return {'success': True}
    elif auth.role == Role.GUEST or auth.role == Role.PAID:
        campaign = models.get_campaign_by_id(id)
        if campaign and campaign.user_id == auth.id:
            campaign = models.delete_campaign(id)
            if campaign:
                return {'success': True}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Campaign not found id")

# # @app.get("/campaigns/{id}/results")
# # async def get_campaign_results(id: int, auth: AuthContext = Depends(auth_token)):
#     auth_permission(auth=auth, roles=(Role.SUPER, Role.ADMIN, Role.AUDITOR))
#     if auth.role == Role.SUPER:


# # @app.get("/campaigns/{id}/summary")
# # async def get_campaign_results(id: int, auth: AuthContext = Depends(auth_token)):
#     auth_permission(auth=auth, roles=(Role.SUPER, Role.ADMIN, Role.AUDITOR))
#     if auth.role == Role.SUPER:

# # @app.get("/campaigns/{id}/complete")
# # async def get_campaign_results(id: int, auth: AuthContext = Depends(auth_token)):
#     auth_permission(auth=auth, roles=(Role.SUPER, Role.ADMIN, Role.AUDITOR))
#     if auth.role == Role.SUPER:

# # @app.get("/campaigns/{id}/launch")
# # async def get_campaign_results(id: int, auth: AuthContext = Depends(auth_token)):
#     auth_permission(auth=auth, roles=(Role.SUPER, Role.ADMIN, Role.AUDITOR))
#     if auth.role == Role.SUPER:

if __name__ == "__main__":
    models.init_org_db()
    uvicorn.run(app, host=os.getenv('HOST'), port=int(os.getenv('PORT')))
