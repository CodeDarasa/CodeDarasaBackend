"""Test cases for user authentication and profile management in a FastAPI application."""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_PREFIX = "/api/v1"


def unique_username():
    """Generate a unique username for testing purposes."""
    return f"user_{uuid.uuid4().hex[:8]}"


def auth_headers(token):
    """Generate authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {token}"}


def unique_name(prefix):
    """Generate a unique name with a given prefix for testing purposes."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def user_token():
    """Fixture to create a user and return an authentication token."""
    username = unique_name("user")
    password = "testpass"
    client.post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    resp = client\
        .post(f"{API_PREFIX}/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]


@pytest.fixture
def category_id(user_token):
    """Fixture to create a category and return its ID."""
    name = unique_name("Category")
    resp = client.post(f"{API_PREFIX}/categories/", json={"name": name},
                       headers={"Authorization": f"Bearer {user_token}"})
    return resp.json()["id"]


@pytest.fixture
def course_id(user_token, category_id):
    """Fixture to create a course and return its ID."""
    title = unique_name("Course")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "desc",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    return resp.json()["id"]


def test_register_and_login():
    """Test user registration and login functionality."""
    username = unique_username()
    password = "testpass"
    # Register
    resp = client\
        .post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    assert resp.status_code in (200, 201)
    # Login
    resp = client\
        .post(f"{API_PREFIX}/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token


def test_register_duplicate_username():
    """Test that registering with a duplicate username fails."""
    username = unique_username()
    password = "testpass"
    client\
        .post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    resp = client\
        .post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    assert resp.status_code in (400, 409)


def test_login_wrong_password():
    """Test that logging in with a wrong password fails."""
    username = unique_username()
    password = "testpass"
    client.post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    resp = client\
        .post(f"{API_PREFIX}/auth/login", json={"username": username, "password": "wrongpass"})
    assert resp.status_code == 401


def test_login_nonexistent_user():
    """Test that logging in with a nonexistent user fails."""
    resp = client\
        .post(f"{API_PREFIX}/auth/login", json={"username": "nonexistent", "password": "nopass"})
    assert resp.status_code == 401


def test_profile_update():
    """Test updating user profile after login."""
    username = unique_username()
    password = "testpass"
    # Register and login
    client.post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    resp = client\
        .post(f"{API_PREFIX}/auth/login", json={"username": username, "password": password})
    token = resp.json()["access_token"]
    # Update profile
    resp = client.put(
        f"{API_PREFIX}/users/me",
        json={"username": "newusername", "full_name": "Jane Doe", "bio": "Test bio"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Jane Doe"
    assert data["bio"] == "Test bio"


def test_profile_update_unauthenticated():
    """Test that updating user profile without authentication fails."""
    resp = client.put(
        f"{API_PREFIX}/users/me",
        json={"full_name": "Jane Doe", "bio": "Test bio"}
    )
    assert resp.status_code == 401


def test_get_profile():
    """Test retrieving user profile after login."""
    username = unique_username()
    password = "testpass"
    client.post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    resp = client\
        .post(f"{API_PREFIX}/auth/login", json={"username": username, "password": password})
    token = resp.json()["access_token"]
    resp = client.get(f"{API_PREFIX}/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == username


def test_get_profile_unauthenticated():
    """Test that retrieving user profile without authentication fails."""
    resp = client.get(f"{API_PREFIX}/users/me")
    assert resp.status_code == 401


def test_get_user_ratings(user_token, course_id):
    """Test retrieving user ratings for a course."""
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 5},
        headers=auth_headers(user_token)
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert len(data) >= 1
