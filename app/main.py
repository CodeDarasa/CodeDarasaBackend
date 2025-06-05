from fastapi import FastAPI
from app.api.routes import auth, courses, categories, users

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

app.include_router(
    categories.router,
    prefix="/api/categories",
    tags=["categories"]
)

app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"]
)
