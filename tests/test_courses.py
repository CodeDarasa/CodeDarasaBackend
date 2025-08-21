"""Test cases for course management API endpoints."""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_PREFIX = "/api/v1"


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


def auth_headers(token):
    """Generate authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {token}"}


def test_create_course_success(user_token, category_id):
    """Test creating a course with valid data."""
    title = unique_name("Course")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "A test course",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["title"] == title
    assert data["category_id"] == category_id
    assert "creator" in data


def test_create_course_unauthenticated(category_id):
    """Test creating a course without authentication."""
    title = unique_name("CourseNoAuth")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "A test course",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        }
    )
    assert resp.status_code == 401


def test_create_course_missing_fields(user_token, category_id):
    """Test creating a course with missing fields."""
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "description": "desc",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 422


def test_get_courses():
    """Test retrieving the list of courses."""
    resp = client.get(f"{API_PREFIX}/courses/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_single_course(user_token, category_id):
    """Test retrieving a single course by ID."""
    title = unique_name("SingleCourse")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "desc",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    course_id = resp.json()["id"]
    resp = client.get(f"{API_PREFIX}/courses/{course_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == course_id
    assert data["title"] == title


def test_get_nonexistent_course():
    """Test retrieving a course that does not exist."""
    resp = client.get(f"{API_PREFIX}/courses/999999")
    assert resp.status_code == 404


def test_update_course(user_token, category_id):
    """Test updating an existing course."""
    # Create course
    title = unique_name("ToUpdate")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "desc",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    course_id = resp.json()["id"]
    # Update course
    new_title = unique_name("Updated")
    resp = client.put(
        f"{API_PREFIX}/courses/{course_id}",
        json={
            "title": new_title,
            "description": "new desc",
            "youtube_url": "https://youtube.com/updated",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == new_title


def test_update_course_unauthenticated(user_token, category_id):
    """Test updating a course without authentication."""
    # Create course
    title = unique_name("ToUpdateNoAuth")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "desc",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    course_id = resp.json()["id"]
    # Try update without auth
    resp = client.put(
        f"{API_PREFIX}/courses/{course_id}",
        json={
            "title": "NoAuth",
            "description": "desc",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        }
    )
    assert resp.status_code == 401


def test_delete_course(user_token, category_id):
    """Test deleting a course."""
    # Create course
    title = unique_name("ToDelete")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "desc",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    course_id = resp.json()["id"]
    # Delete course
    resp = client.delete(f"{API_PREFIX}/courses/{course_id}", headers=auth_headers(user_token))
    assert resp.status_code in (200, 204)


def test_delete_course_unauthenticated(user_token, category_id):
    """Test deleting a course without authentication."""
    # Create course
    title = unique_name("ToDeleteNoAuth")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "desc",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    course_id = resp.json()["id"]
    # Try delete without auth
    resp = client.delete(f"{API_PREFIX}/courses/{course_id}")
    assert resp.status_code == 401


def test_filter_courses_by_category(user_token, category_id):
    """Test filtering courses by category."""
    # Create a course in this category
    title = unique_name("CourseFilter")
    client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "A test course",
            "youtube_url": "https://youtube.com/test",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    # Filter by category
    resp = client.get(f"{API_PREFIX}/courses/?category_id={category_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert any(course["category_id"] == category_id for course in data)
