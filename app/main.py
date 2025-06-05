from fastapi import FastAPI
from app.api.routes import courses

app = FastAPI(title="Code Darasa API")

app.include_router(courses.router, prefix="/api")
