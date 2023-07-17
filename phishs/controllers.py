from httpx import AsyncClient
from fastapi import Request, HTTPException, status
from dotenv import load_dotenv
from schemas import (Role, AuthContext, EmailSchema, CampaignManager,
                     CampaignSchema, Target, TemplateReqModel, EmailReqModel)
from random import choices
import os

load_dotenv()
TEMPLATES_URI = os.getenv('TEMPLATES_URI')
MAILFUNC_URI = os.getenv('MAILFUNC_URI')
API_KEY = os.getenv('API_KEY')

running_campaign: dict[str, CampaignManager] = dict()


def get_random_ref():
    ref = ''.join(
        choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXVZ0123456789', k=4))
    while ref in running_campaign:
        ref = ''.join(
            choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXVZ0123456789', k=4))
    return ref


def process_before_launch(campaign: CampaignSchema, targets: list[Target]):
    ref = get_random_ref()
    c = CampaignManager(id=campaign.id,
                        ref=ref,
                        start_date=campaign.launch_date,
                        end_date=campaign.send_by_date,
                        targets=targets)
    for t in c.targets:
        t.ref = get_random_ref()
    running_campaign[ref] = c
    return c


async def launch_template_worker(req: TemplateReqModel, auth: AuthContext):
    async with AsyncClient() as client:
        try:
            json = {'api_key': API_KEY}
            json.update(req.dict())
            json.update(auth.dict())
            res = await client.post(TEMPLATES_URI, json=json)
            if res.status_code == 200:
                res = res.json()
                return EmailSchema(**res)
            elif res.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="INTERNAL SERVER ERROR, Cannot get Templates")
            elif res.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not Found")
            else:
                raise Exception()
        except HTTPException as e:
            raise e
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR, Cannot get Templates")


async def launch_email_worker(req: EmailReqModel, auth: AuthContext):
    pass
