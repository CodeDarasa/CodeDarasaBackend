from fastapi import FastAPI
from app.api.routes import auth, courses

app = FastAPI(title="Code Darasa Backend")

app.include_router(
    courses.router,
    prefix="/api/courses",
    tags=["courses"]
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["auth"]
)
