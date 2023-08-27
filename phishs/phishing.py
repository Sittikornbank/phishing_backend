import uvicorn
from datetime import datetime
from fastapi import Request, FastAPI, status, HTTPException, Depends, Body
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthContext, get_token, protect_api
import schemas
from controllers import (launch_template, process_before_launch,
                         launch_email, stop_template, stop_campaign,
                         handle_event, write_log)
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000"],
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
async def launch(model: schemas.LaunchModel, _=Depends(protect_api)):
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
            targets_str = ["\n"+str(s.dict()) for s in c.targets]
            write_log(c.ref, [f'launch campaign: {model.campaign.id}',
                              f'template: {model.campaign.templates_id}',
                              f'smtp: {model.campaign.smtp_id}',
                              f'url : {email_temp.base_url}',
                              f'targets : {targets_str}']
                      )
            return {'ref_key': c.ref, 'targets': c.targets, 'payload': {'envelope_sender': email_temp.envelope_sender, 'base_url': email_temp.base_url,
                                                                        're_url': email_temp.redirect_url, 'capture_cred': email_temp.capture_credentials,
                                                                        'capture_pass': email_temp.capture_passwords}}

    except HTTPException as e:
        await stop_template(ref_key=c.ref, auth=model.auth)
        raise e
    await stop_template(ref_key=c.ref, auth=model.auth)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Fail to Launch Campaign'
    )


def calculate_duration(start: datetime | None, stop: datetime | None):
    if not stop or not start:
        return 0
    differ = int(stop.timestamp()) - int(start.timestamp())
    if differ < 0:
        return 0
    return differ


@app.post('/event')
async def email_event(e: schemas.EventContext, _=Depends(protect_api)):
    if e.sender in ['email', 'site']:
        res = await handle_event(context=e)
        if res:
            return {'success': res}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Task not found'
    )


@app.post('/complete')
async def complete(camp: schemas.CompleteSchema, _=Depends(protect_api)):
    res = await stop_campaign(campaign_id=camp.campaign_id, auth=camp.auth)
    return {'success': res}


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv('HOST'), port=int(os.getenv('PORT')))
