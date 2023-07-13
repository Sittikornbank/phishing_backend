from models import Phishsite, get_phishsite_by_id
from dotenv import load_dotenv
from time import time
import jwt
import os

load_dotenv()

SECRET = os.getenv("SECRET")
