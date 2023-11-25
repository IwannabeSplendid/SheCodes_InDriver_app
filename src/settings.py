import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings


env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # Database
    DB_USER: str = os.getenv('DB_USER')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD')
    DB_NAME: str = os.getenv('DB_NAME')
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: str = os.getenv('DB_PORT')
    DATABASE_URL: str = f"postgresql+psycopg2://{DB_NAME}:%s@{DB_HOST}:{DB_PORT}/{DB_NAME}" % quote_plus(DB_PASSWORD)
    
    # External Database
    SUPABASE_KEY: str = os.getenv('SUPABASE_KEY')
    SUPABASE_URL: str = os.getenv('SUPABASE_URL')
    
    # Whatsapp access token 
    WHATSAPP_TOKEN: str = os.getenv('WHATSAPP_TOKEN')
    
    # ChatGPT secret
    CHATGPT_SECRET: str = os.getenv('CHATGPT_API_SECRET')
    
    # JWT 
    JWT_SECRET: str = os.getenv('JWT_SECRET')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('JWT_TOKEN_EXPIRE_MINUTES')


def get_settings() -> Settings:
    return Settings()
