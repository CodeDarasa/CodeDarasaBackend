"""Configuration settings for the application."""
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

ENV = os.getenv("ENV", "app")
SQLALCHEMY_DATABASE_URL = ""

if ENV == "test":
    SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")


class Settings:
    """Application settings class that holds configuration values."""
    DATABASE_URL: str = SQLALCHEMY_DATABASE_URL
    SECRET_KEY: str = os.getenv("SECRET_KEY")


settings = Settings()
