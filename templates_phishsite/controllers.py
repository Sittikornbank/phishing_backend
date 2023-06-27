import uvicorn
from fastapi import FastAPI, status, HTTPException, Depends
from users.auth import get_token, check_permission, check_token
from models import *
from db import SessionLocal, engine, Base
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/templates")
async def get_templates(token: str = Depends(get_token),db: Session = Depends(get_db)):
    role = await check_permission(token,roles=PERMIT.ALL)
    try:
        templates = get_ts(db)
        ts = []
        for t in templates:
            print(t.visible)
            temp = EmailTemplate(id=t.id,name=t.name,html=t.html,
                                            modified_date=t.modified_date,
                                            visible=t.visible,envelope_sender=t.envelope_sender,
                                            subject=t.subject,attachments=list(t.attachments))
            if role in PERMIT.PAID.value:
                if t.visible != VISIBLE.NONE or role in PERMIT.SUPER.value:
                    ts.append(temp)
            elif t.visible != VISIBLE.NONE.value:
                if t.visible == VISIBLE.PAID.value:
                    temp.html = None
                ts.append(temp)
        return ts
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )


@app.get("/templates/{tid}")
async def get_template(tid:int, token: str = Depends(get_token),db: Session = Depends(get_db)):
    role = await check_permission(token,roles=PERMIT.ALL)
    try:
        t = get_t(db,tid)
        temp = EmailTemplate(id=t.id,name=t.name,html=t.html,
                            modified_date=t.modified_date,
                            visible=t.visible,envelope_sender=t.envelope_sender,
                            subject=t.subject,attachments=list(t.attachments))
        if role in PERMIT.PAID.value:
            if t.visible != VISIBLE.NONE or role in PERMIT.SUPER.value:
                return temp
        elif t.visible != VISIBLE.NONE.value:
            if t.visible == VISIBLE.PAID.value:
                temp.html = None
                return temp
    except Exception as e:
         print(e)
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    

@app.post("/templates")
async def create_template(email: EmailTemplate,
                          token: str = Depends(get_token),
                          db: Session = Depends(get_db),):
    role = await check_permission(token,roles=PERMIT.SUPER)
    temp = create_t(db,email)
    return {
        'id': temp.id,
        'name':temp.name,
        'html':temp.html,
        'envelope_sender':temp.envelope_sender,
        'subject':temp.subject,
        'attachments':temp.attachments,
        'visible':temp.visible
    }

@app.put("/templates/{tid}")
async def update_template(tid:int,
                          email: TemplateUpdate,
                          token: str = Depends(get_token),
                          db: Session = Depends(get_db)):
    await check_permission(token,roles=PERMIT.SUPER)
    temp = dict()
    if email.name:
        temp['name'] = email.name
    if email.html:
        temp['html'] = email.html
    if email.envelope_sender:
        temp['envelope_sender'] = email.envelope_sender
    if email.subject:
        temp['subject'] = email.subject
    if email.attachments:
        temp['attachments'] = email.attachments
    if email.visible:
        temp['visible'] = email.visible.value
    try:
        temp = update_t(db,tid,temp)
        return {
            'id': temp.id,
            'name':temp.name,
            'html':temp.html,
            'envelope_sender':temp.envelope_sender,
            'subject':temp.subject,
            'attachments':temp.attachments,
            'visible':temp.visible
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )



@app.delete("/templates/{tid}")
async def delete_template(tid:int, token: str = Depends(get_token),db: Session = Depends(get_db)):
    await check_permission(token,roles=PERMIT.SUPER)
    try:
        delete_t(db,tid)
        return {'success':True}
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=60502)