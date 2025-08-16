from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, courses, categories, comments, ratings, users

app = FastAPI(
    title="CodeDarasa API",
    description="Code Darasa Backend",
    version="1.0.0"
)

# Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
