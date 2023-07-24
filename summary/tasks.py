from httpx import AsyncClient
from fastapi import HTTPException, status
from schemas import EVENT, EventModel, AuthContext
from models import add_event, Campaign, Target
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

PHISHING_URI = os.getenv('PHISHING_URI')


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
        json = dict()
        json['auth'] = auth
        json['campaign'] = campaign
        json['target'] = targets

        try:
            res = await client.post(PHISHING_URI, json=json)
            data = res.json()
            if res.status_code == 200 and data['success']:
                return True
            else:
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
