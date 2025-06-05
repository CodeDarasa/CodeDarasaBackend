from fastapi import FastAPI
from app.api.routes import courses

app = FastAPI(title="Code Darasa Backend")

app.include_router(
    courses.router,
    prefix="/api/courses",
    tags=["courses"]
)
