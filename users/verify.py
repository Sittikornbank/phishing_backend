import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

SECRET = os.getenv("VERIFY_SECRET")
EXPIRE_HOURS = os.getenv("VERIFY_EMAIL_EXPIRE_HOURS")


def create_verify_token(user_id: int):
    return jwt.encode({"user_id": user_id,
                       "exp": datetime.utcnow() + timedelta(hours=EXPIRE_HOURS)},
                      SECRET, algorithm="HS256")


def read__verify_token(token: str):
    return jwt.decode(token, SECRET, algorithms=["HS256"])


def send_verify_email(to_email: str, user_id: int):
    verification_token = create_verify_token(user_id)
    # กำหนดข้อมูลการส่งอีเมล (ผู้ส่ง, ผู้รับ, หัวข้อ, ข้อความ)
    from_email = '<noreply>@tummainorrr.com'
    subject = 'Verification Email'
    message = 'Thank you for singed up to our service.\n' + \
        f'Click here to verify your Email: http://127.0.0.1:50501/verify?code={verification_token}' + \
        f'\nPlease verify your email within {EXPIRE_HOURS} hour(s).'

    # สร้างอีเมล
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # เพิ่มข้อความในอีเมล
    msg.attach(MIMEText(message, 'plain'))

    # ส่งอีเมล
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    username = os.getenv('VERIFY_EMAIL_USERNAME')
    password = os.getenv('VERIFY_EMAIL_PASSWORD')
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(from_email, to_email, msg.as_string())
