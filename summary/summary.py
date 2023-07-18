from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
from fastapi import FastAPI
from sqlalchemy.orm import Session
import uvicorn
from fastapi import Request, FastAPI
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from models import (Base, engine, get_db, get_group_by_id, create_group)
import os
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import schemas
import models

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
async def get_group_configss(page: int | None = 1, limit: int | None = 25):
    # if empty in database --> Show {"count": 1,page": 1,"last_page": 2,"limit": 1,"smtp": []}
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


@app.put('/groups/{id}', response_model=schemas.GroupDisplayModel)
async def modify_group(id: int, temp_in: schemas.GroupFormModel):
    t = dict()
    t['modified_date'] = datetime.now()
    if temp_in.name:
        t['name'] = temp_in.name
    if temp_in.targets != None:
        t['targets'] = temp_in.targets
        print(temp_in.targets)
    temp = models.update_group(t, id)
    if temp:
        return temp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not Found"
    )


# @app.put('/groups/{id}', response_model=schemas.GroupDisplayModel)
# async def update_group(id: int, group_data: schemas.GroupFormModel):
#     db = next(get_db())
#     try:
#         group = models.get_group_by_id(id)
#         if not group:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

#         # Update group properties if provided in the request body
#         if group_data.name is not None:
#             group.name = group_data.name
#         if group_data.modified_date is not None:
#             group.modified_date = group_data.modified_date

#         # Update the targets of the group
#         if group_data.targets is not None:
#             group_targets = models.get_targets(group.id)
#             existing_emails = {target.email for target in group_targets}
#             for new_target in group_data.targets:
#                 if new_target.email in existing_emails:
#                     # If the target already exists, update its information.
#                     existing_target = db.query(models.Target).filter_by(
#                         email=new_target.email).first()
#                     existing_target.first_name = new_target.first_name
#                     existing_target.last_name = new_target.last_name
#                     existing_target.position = new_target.position
#                 else:
#                     # Otherwise, add the new target to the group.
#                     target = models.Target(first_name=new_target.first_name, last_name=new_target.last_name,
#                                            email=new_target.email, position=new_target.position)
#                     db.add(target)
#                     db.commit()
#                     db.refresh(target)
#                     models.insert_target_into_group(db, target, group.id)

#         # Commit the changes to the database
#         db.commit()
#         db.refresh(group)

#         return group

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                             detail="An error occurred while updating the group")
#     finally:
#         db.close()


# @app.delete('/site_templates/{temp_id}')
# async def del_site_template(temp_id: int, token: str = Depends(get_token)):
#     await check_permission(token, (Role.SUPER,))
#     temp = models.get_site_template_by_id(temp_id)
#     if temp:
#         if temp.image_site:
#             image_path = os.path.join(IMAGES_FOLDER, temp.image_site)
#             if os.path.exists(image_path):
#                 os.remove(image_path)

#         models.delete_site_temp(temp_id)
#         return {'success': True}
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="Not Found"
#     )


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv('HOST'), port=os.getenv('PORT'))
