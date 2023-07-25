from httpx import AsyncClient
from fastapi import HTTPException, status
from schemas import EVENT, EventModel, AuthContext, CampaignSendModel, TargetModel
from models import add_event, Campaign, Target
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

PHISHING_URI = os.getenv('PHISHING_URI')
API_KEY = os.getenv('API_KEY')


async def stop_campaign_tasks(campaign: Campaign):
    update_stats(EventModel(
        campaign_id=campaign.id,
        target_id=None,
        email=None,
        time=datetime.now(),
        message=EVENT.COMPLETE,
        details=None
    ))


def update_stats(event: EventModel):
    add_event(event)


async def lanuch_campaign(campaign: Campaign, targets: list[Target], auth: AuthContext):
    async with AsyncClient() as client:
        campaign = CampaignSendModel(**campaign.__dict__).dict()
        campaign['launch_date'] = datetime.now().isoformat()
        if campaign['send_by_date']:
            campaign['send_by_date'] = campaign['send_by_date'].isoformat()
        targets = [TargetModel(**t.__dict__).dict() for t in targets]
        json = dict()
        json['auth'] = auth.dict()
        json['campaign'] = campaign
        json['targets'] = targets

        header = {'Authorization': f'Bearer {API_KEY}'}

        try:
            res = await client.post(PHISHING_URI+'/launch', json=json, headers=header)
            data = res.json()
            if res.status_code == 200 and data['success']:
                return True
            elif 'detail' in data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Cannot Launch, {data['detail']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR, Cannot Launch")
        except HTTPException as e:
            raise e
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR")


async def complete_campaign(campaign: Campaign):
    async with AsyncClient() as client:
        json = {'campaign': campaign.id}
        header = {'Authorization': f'Bearer {API_KEY}'}
        try:
            res = await client.post(PHISHING_URI+'/complete', json=json, headers=header)
            data = res.json()
            if res.status_code == 200 and data['success']:
                return True
            elif 'detail' in data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Cannot Camplete, {data['detail']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR, Cannot Camplete")
        except HTTPException as e:
            raise e
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL SERVER ERROR")
