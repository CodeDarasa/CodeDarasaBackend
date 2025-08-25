"""Configuration settings for the application."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "app")
SQLALCHEMY_DATABASE_URL = ""

if ENV == "test":
    SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")


@dataclass
class Settings:
    """Application settings class that holds configuration values."""
    database_url: str = SQLALCHEMY_DATABASE_URL
    secret_key: str = os.getenv("SECRET_KEY", "test-key")


settings = Settings()
