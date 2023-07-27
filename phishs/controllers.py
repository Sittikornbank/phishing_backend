from httpx import AsyncClient
from fastapi import Request, HTTPException, status
from dotenv import load_dotenv
from schemas import (Role, AuthContext, EmailSchema, CampaignManager,
                     CampaignSchema, Target, TemplateReqModel, EmailReqModel,
                     EventContext, EventType, EventOutModel)
from random import choices
import os
from string import ascii_letters, digits

load_dotenv()
TEMPLATES_URI = os.getenv('TEMPLATES_URI')
MAILFUNC_URI = os.getenv('MAILFUNC_URI')
CALLBACK_URI = os.getenv('CALLBACK_URI')
API_KEY = os.getenv('API_KEY')

running_campaign: dict[str, CampaignManager] = dict()


def get_campaign_manager_by_id(id: int):
    for c in running_campaign:
        if running_campaign[c].id == id:
            return c, running_campaign[c]


def get_random_ref(check_set: set[str] = set()):
    s = ascii_letters+digits
    ref = ''.join(choices(s, k=4))
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
                        targets=targets,
                        target_index_set=dict())
    check = set()
    for t in c.targets:
        t.ref = get_random_ref(check)
        c.target_index_set[t.ref] = (set(), t.email)
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
            json = ({'ref_key': ref_key, 'auth': auth.dict()})
            res = await client.request(method='DELETE', url=TEMPLATES_URI, json=json, headers=header)
            return res.json()['success']
        except Exception as e:
            print(e)
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
            json = {'auth': auth.dict(), 'ref_key': ref_key}
            res = await client.request(method='DELETE', url=MAILFUNC_URI, json=json, headers=header)
            return res.json()['success']
        except Exception as e:
            print(e)
    return False


async def stop_campaign(campaign_id: int, auth: AuthContext):
    ref_key, campaign = get_campaign_manager_by_id(campaign_id)
    if ref_key and campaign:
        await stop_email(ref_key=ref_key, auth=auth)
        await stop_template(ref_key=ref_key, auth=auth)
        running_campaign.pop(ref_key)
        return True
    return False


async def handle_event(context: EventContext):
    if context.sender == 'email' and not context.event_type in (EventType.FAIL, EventType.SEND, EventType.REPORT):
        return False
    if context.sender == 'site' and not context.event_type in (EventType.CLICK, EventType.OPEN, EventType.SUBMIT):
        return False
    if not context.ref_key in running_campaign:
        return False
    campaign_mgr = running_campaign[context.ref_key]
    if not context.ref_id in campaign_mgr.target_index_set:
        return False
    if context.event_type in campaign_mgr.target_index_set[context.ref_id][0]:
        return False
    res = await callback_event(EventOutModel(
        campaign_id=campaign_mgr.id,
        r_id=context.ref_key+context.ref_id,
        email=campaign_mgr.target_index_set[context.ref_id][1],
        event=context.event_type,
        details=context.payload
    ))
    if res:
        campaign_mgr.target_index_set[context.ref_id].add(context.event_type)
        return True
    return False


async def callback_event(e: EventOutModel):
    async with AsyncClient() as client:
        try:
            header = {'Authorization': f'Bearer {API_KEY}'}
            res = await client.post(CALLBACK_URI, json=e.dict(), headers=header)
            data = res.json()
            if res.status_code == 200 and data['success']:
                return True
        except Exception as e:
            print(e)
        return False
