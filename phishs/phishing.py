import uvicorn
from datetime import datetime
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthContext, get_token, protect_api
import schemas
from controllers import (launch_template, process_before_launch,
                         launch_email, stop_template)
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI()


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


@app.post('/launch')
async def launch(model: schemas.LaunchModel, _=Depends(get_token)):
    c = process_before_launch(
        model.campaign, targets=model.targets, auth=model.auth)
    reqt = schemas.TemplateReqModel(ref_key=c.ref,
                                    ref_ids=[t.ref for t in c.targets],
                                    template_id=model.campaign.templates_id,
                                    start_at=int(model.campaign.launch_date.timestamp()))
    email_temp = await launch_template(req=reqt, auth=model.auth)
    duration = calculate_duration(
        model.campaign.launch_date, model.campaign.send_by_date)
    reqm = schemas.EmailReqModel(task_id=c.ref,
                                 smtp_id=model.campaign.smtp_id,
                                 sender=email_temp.envelope_sender,
                                 html=email_temp.html,
                                 subject=email_temp.subject,
                                 attachments=email_temp.attachments,
                                 duration=duration,
                                 targets=c.targets,
                                 base_url=email_temp.base_url
                                 )
    try:
        res = await launch_email(req=reqm, auth=model.auth)
        if res:
            return {'success': True}
    except HTTPException as e:
        await stop_template(ref_key=c.ref, auth=model.auth)
        raise e
    await stop_template(ref_key=c.ref, auth=model.auth)
    return {'success': False}


def calculate_duration(start: datetime, stop: datetime):
    differ = int(stop.timestamp()) - int(start.timestamp())
    if differ < 0:
        return 0
    return differ

# @app.post('/event/email')
# @app.post('/event/site')
# @app.post('/complete')


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv('HOST'), port=int(os.getenv('PORT')))
