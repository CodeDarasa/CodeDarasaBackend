from fastapi import FastAPI
from app.api.routes import auth, courses, categories, users

app = FastAPI(
    title="CodeDarasa API",
    description="Code Darasa Backend",
    version="1.0.0"
)

# Versioned API prefix
API_PREFIX = "/api/v1"

app.include_router(
    courses.router,
    prefix=f"{API_PREFIX}/courses",
    tags=["courses"]
)

app.include_router(
    auth.router,
    prefix=f"{API_PREFIX}/auth",
    tags=["auth"]
)

app.include_router(
    categories.router,
    prefix=f"{API_PREFIX}/categories",
    tags=["categories"]
)

app.include_router(
    users.router,
    prefix=f"{API_PREFIX}/users",
    tags=["users"]
)

from app.api.routes import comments, ratings

app.include_router(
    comments.router, 
    prefix=f"{API_PREFIX}", 
    tags=["comments"]
)

app.include_router(
    ratings.router, 
    prefix=f"{API_PREFIX}", 
    tags=["ratings"]
)
