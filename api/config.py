import pathlib
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

# class Settings(BaseSettings):
#     db_host: str
#     db_port: int
#     db_username: str
#     db_password: str
#     db_name: str
#     mail_username: str
#     mail_password: str
#     mail_from: str
#     mail_server: str
#     mail_port: int


#     class Config:
#         env_file = f"{pathlib.Path(__file__).resolve().parent}/.env"

class Settings(BaseSettings):
    db_host: str = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT", 5433))
    db_username: str = os.getenv("DB_USERNAME")
    db_password: str = os.getenv("DB_PASSWORD")
    db_name: str = os.getenv("DB_NAME")
    
    mail_username: str = os.getenv("MAIL_USERNAME")
    mail_password: str = os.getenv("MAIL_PASSWORD")
    mail_from: str = os.getenv("MAIL_FROM")
    mail_server: str = os.getenv("MAIL_SERVER")
    mail_port: int = int(os.getenv("MAIL_PORT", 587))

    class Config:
        env_file = f"{pathlib.Path(__file__).resolve().parent}/.env"
    
def get_settings():
    return Settings()

get_settings()