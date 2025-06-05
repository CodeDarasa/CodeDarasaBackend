# Code Darasa Backend – Project Context for Copilot

Code Darasa is an edtech platform for sharing programming tutorials and full video-based courses. This backend is built using FastAPI and PostgreSQL, with SQLAlchemy for ORM and Alembic for migrations.

### Key Features
- Course management: create and list courses
- Embedded YouTube video support (initially), with plans for custom video hosting
- Clean, modular structure: `app/api`, `crud`, `db`, `schemas`, and `core`
- Secure, scalable, and ready to be extended (auth, categories, file uploads, etc.)

### Tech Stack
- Flask (web framework)
- PostgreSQL (database)
- SQLAlchemy (ORM)
- Alembic (migrations)
- Pydantic (data validation)

### API Endpoints
- `POST /api/courses/` – Create a course with title, description, and YouTube URL
- `GET /api/courses/` – List available courses with pagination
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

settings = Settings()
This backend will power a future frontend (web app) and mobile clients. All course data will be stored here, and eventually video streaming and user accounts will be handled on this platform.

