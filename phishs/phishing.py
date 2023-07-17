import uvicorn
from datetime import datetime
from fastapi import Request, FastAPI, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthContext, get_token
import schemas
from controllers import launch_template_worker, process_before_launch
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
async def launch(model: schemas.LaunchModel, token=Depends(get_token)):
    c = process_before_launch(model.campaign, targets=model.targets)
    reqt = schemas.TemplateReqModel(task_ref=c.ref,
                                    refs=[t.ref for t in c.targets],
                                    template_id=model.campaign.templates_id,
                                    start_at=int(model.campaign.launch_date.timestamp()))
    email_temp = await launch_template_worker(req=reqt, auth=model.auth)
    try:
        pass
    except:
        pass

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv('HOST'), port=os.getenv('PORT'))
