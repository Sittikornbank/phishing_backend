from httpx import AsyncClient
from fastapi import Request, HTTPException, status
from dotenv import load_dotenv
from schemas import (Role, AuthContext, EmailSchema, CampaignManager,
                     CampaignSchema, Target, TemplateReqModel, EmailReqModel)
from random import choices
import os
from string import ascii_letters, digits

load_dotenv()
TEMPLATES_URI = os.getenv('TEMPLATES_URI')
MAILFUNC_URI = os.getenv('MAILFUNC_URI')
API_KEY = os.getenv('API_KEY')

running_campaign: dict[str, CampaignManager] = dict()


def get_random_ref(check_set: set[str] = set()):
    ref = ''.join(choices(ascii_letters+digits, k=4))
    if not check_set:
        while ref in running_campaign:
            ref = ''.join(choices(s, k=4))
    else:
        while ref in check_set:
            ref = ''.join(choices(s, k=4))
            set.add(ref)
    return ref


def process_before_launch(campaign: CampaignSchema, auth: AuthContext, targets: list[Target]):
    if auth.role in [Role.GUEST, Role.PAID] and campaign.user_id != auth.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannont access the Campaign")
    if auth.role == Role.ADMIN and campaign.org_id != auth.organization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannont access the Campaign")
    if auth.role == Role.AUDITOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannont access the Campaign")
    if len(targets) == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Campaign has no targets")
    ref = get_random_ref()
    c = CampaignManager(id=campaign.id,
                        ref=ref,
                        start_date=campaign.launch_date,
                        end_date=campaign.send_by_date,
                        targets=targets)
    check = set()
    for t in c.targets:
        t.ref = get_random_ref(check)
    running_campaign[ref] = c
    return c


async def launch_template(req: TemplateReqModel, auth: AuthContext):
    async with AsyncClient() as client:
        try:
            header = {'Authorization': f'Bearer {API_KEY}'}
            json = {'req': req.dict(), 'auth': auth.dict()}
            res = await client.post(TEMPLATES_URI, json=json, headers=header)
            if res.status_code == 200:
                res = res.json()
                return EmailSchema(**res)
            elif res.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Cannot Use Template")
            elif res.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not Found")
            elif res.status_code == 406:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Template not Complete")
            else:
                raise Exception()
        except HTTPException as e:
            raise e
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR, Cannot get Templates")


async def stop_template(ref_key: str, auth: AuthContext):
    async with AsyncClient() as client:
        try:
            header = {'Authorization': f'Bearer {API_KEY}'}
            json = auth.dict()
            json.update({'ref_key': ref_key})
            res = await client.request(method='DELETE', url=TEMPLATES_URI, json=json, headers=header)

        except Exception as e:
            print(e)
            print(res.json())
    return False


async def launch_email(req: EmailReqModel, auth: AuthContext):
    async with AsyncClient() as client:
        try:
            header = {'Authorization': f'Bearer {API_KEY}'}
            json = req.dict()
            json.update({'auth': auth.dict()})
            res = await client.post(MAILFUNC_URI, json=json, headers=header)
            if res.status_code == 200:
                res = res.json()
                return res['success']
            elif res.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Cannot Start Sending Emails")
            elif res.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cannot Start Sending Emails")
            else:
                raise Exception()
        except HTTPException as e:
            raise e
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR, Cannot start sending Email")


async def stop_email(ref_key: str, auth: AuthContext):
    async with AsyncClient() as client:
        try:
            header = {'Authorization': f'Bearer {API_KEY}'}
            json = auth.dict()
            json.update({'ref_key': ref_key})
            res = await client.request(method='DELETE', url=MAILFUNC_URI, json=json, headers=header)
            print(res.json())
        except Exception as e:
            print(e)
    return False
