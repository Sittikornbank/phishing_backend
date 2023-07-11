import jwt
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

secret = os.getenv("VERIFY_SECRET")


def create_verify_token(user_id: int):
    return jwt.encode({"user_id": user_id, "create_at": int(time.time())}, secret, algorithm="HS256")
    # print(encoded_jwt)


def read__verify_token(token: str):
    data = jwt.decode(token, secret, algorithms=["HS256"])
    create_at = data['create_at']
    if (int(time.time()) - create_at) < 3600:
        return data
    return


def send_verify_email(to_email: str, user_id: int):
    verification_email = create_verify_token(user_id)
    # กำหนดข้อมูลการส่งอีเมล (ผู้ส่ง, ผู้รับ, หัวข้อ, ข้อความ)
    from_email = 'tummainorrr.com'
    subject = 'Verification Email'
    message = f'Your verification email : http://127.0.0.1:50501/verify?code={verification_email}'

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
    username = 'tummainorrr@gmail.com'
    password = 'haqyzvueeatcgovh'
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(from_email, to_email, msg.as_string())
