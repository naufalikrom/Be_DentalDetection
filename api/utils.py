import pyotp 
from passlib.context import CryptContext
from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema,MessageType
from typing import List
from .config import get_settings

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt


# Secret Key untuk JWT
SECRET_KEY = "dentalDetection"  # Ganti dengan secret key yang lebih aman
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = get_settings()

#hash passowrd
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password:str):
    return pwd_context.hash(password)
def verify_password(rw_password:str, hashed_password:str):
    return pwd_context.verify(rw_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))  # ✅ Fix
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


conf = ConnectionConfig( 
    MAIL_USERNAME = f"{settings.mail_username}",
    MAIL_PASSWORD = f"{settings.mail_password}",
    MAIL_FROM = f"{settings.mail_from}",
    MAIL_PORT = 587,
    MAIL_SERVER = f"{settings.mail_server}",
    MAIL_STARTTLS = True,  # Aktifkan TLS
    MAIL_SSL_TLS = False,  # Jangan pakai SSL jika pakai TLS
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
def send_email(subject: str,recipients: List, background_tasks: BackgroundTasks, message: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=message,
        subtype="html",
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    
    
secret = pyotp.random_base32()
time_otp=pyotp.TOTP(secret, interval=180)
def generate_otp_code():
    otp=time_otp.now()
    return otp

def verify_otp(otp):
    return time_otp.verify(otp)
