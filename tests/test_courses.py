"""Test cases for course management API endpoints."""
import time
import uuid
from datetime import datetime, timezone

import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.db.models.course import Course

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


def test_create_duplicate_course(user_token, category_id):
    """Test creating a duplicate course (same title and youtube_url)."""
    title = unique_name("DupCourse")
    payload = {
        "title": title,
        "description": "desc",
        "youtube_url": "https://youtube.com/dup",
        "category_id": category_id
    }
    resp1 = client.post(f"{API_PREFIX}/courses/", json=payload, headers=auth_headers(user_token))
    assert resp1.status_code in (200, 201)
    resp2 = client.post(f"{API_PREFIX}/courses/", json=payload, headers=auth_headers(user_token))
    assert resp2.status_code == 400
    assert "already exists" in resp2.json()["detail"]


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


def test_update_nonexistent_course(user_token, category_id):
    """Test updating a course that does not exist."""
    resp = client.put(
        f"{API_PREFIX}/courses/999999",
        json={
            "title": "DoesNotExist",
            "description": "desc",
            "youtube_url": "https://youtube.com/doesnotexist",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_update_course_to_duplicate(user_token, category_id):
    """Test updating a course to match another existing course's details."""
    # Create two courses
    title1 = unique_name("DupA")
    title2 = unique_name("DupB")
    url1 = "https://youtube.com/dupa"
    url2 = "https://youtube.com/dupb"
    resp1 = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title1,
            "description": "desc1",
            "youtube_url": url1,
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    resp2 = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title2,
            "description": "desc2",
            "youtube_url": url2,
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    course_id2 = resp2.json()["id"]
    # Try to update course2 to have same title and url as course1
    resp = client.put(
        f"{API_PREFIX}/courses/{course_id2}",
        json={
            "title": title1,
            "description": "desc1",
            "youtube_url": url1,
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


def test_update_course_to_nonexistent_category(user_token, category_id):
    """Test updating a course to a category that does not exist."""
    # Create a course
    title = unique_name("ToBadCat")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "desc",
            "youtube_url": "https://youtube.com/badcat",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    course_id = resp.json()["id"]
    # Try to update to a non-existent category
    resp = client.put(
        f"{API_PREFIX}/courses/{course_id}",
        json={
            "title": title,
            "description": "desc",
            "youtube_url": "https://youtube.com/badcat",
            "category_id": 999999
        },
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 404
    assert "category not found" in resp.json()["detail"].lower()


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


def test_delete_nonexistent_course(user_token):
    """Test deleting a course that does not exist."""
    resp = client.delete(f"{API_PREFIX}/courses/999999", headers=auth_headers(user_token))
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_delete_course_not_authorized(user_token, category_id):
    """Test deleting a course you are not authorized to delete."""
    # User 1 creates a course
    title = unique_name("NotYourCourse")
    resp = client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": title,
            "description": "desc",
            "youtube_url": "https://youtube.com/notyourcourse",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    course_id = resp.json()["id"]
    # Register a different user
    username2 = unique_name("user2")
    password2 = "testpass2"
    client.post(f"{API_PREFIX}/auth/register", json={"username": username2, "password": password2})
    resp2 = client.post(f"{API_PREFIX}/auth/login", json={"username": username2, "password": password2})
    token2 = resp2.json()["access_token"]
    # Try to delete the course as the other user
    resp = client.delete(f"{API_PREFIX}/courses/{course_id}", headers=auth_headers(token2))
    assert resp.status_code == 403
    assert "not authorized" in resp.json()["detail"].lower()


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


def test_list_courses_with_search(user_token, category_id):
    """Test listing courses using a search term."""
    unique_title = unique_name("SearchableCourse")
    client.post(
        f"{API_PREFIX}/courses/",
        json={
            "title": unique_title,
            "description": "desc",
            "youtube_url": "https://youtube.com/searchable",
            "category_id": category_id
        },
        headers=auth_headers(user_token)
    )
    resp = client.get(f"{API_PREFIX}/courses/?search={unique_title}")
    assert resp.status_code == 200
    data = resp.json()
    assert any(course["title"] == unique_title for course in data)


def test_course_get_id_and_to_dict():
    """Test the get_id and to_dict methods of the Course model."""
    from datetime import datetime, timezone
    from app.db.models.course import Course
    from app.db.models.category import Category
    from app.db.models.user import User

    now = datetime.now(timezone.utc)
    # Related objects (not persisted, just constructed)
    category = Category(id=5, name="Cat5")
    creator = User(id=7, username="creator7", hashed_password="x")

    course = Course(
        id=101,
        title="Test Course",
        description="A test course",
        youtube_url="https://youtube.com/test",
        category_id=5,
        creator_id=7,
        created_at=now,
        updated_at=now,
    )
    course.category = category
    course.creator = creator

    # Test get_id
    assert course.get_id() == 101

    # Test to_dict
    d = course.to_dict()
    assert isinstance(d, dict)
    assert d["id"] == 101
    assert d["title"] == "Test Course"
    assert d["description"] == "A test course"
    assert d["youtube_url"] == "https://youtube.com/test"
    assert d["category_id"] == 5
    assert isinstance(d["category"], dict)
    assert d["category"]["id"] == 5
    assert d["creator_id"] == 7
    assert isinstance(d["creator"], dict)
    assert d["creator"]["id"] == 7
    assert d["created_at"] == now.isoformat()
    assert d["updated_at"] == now.isoformat()

    # Also test with no related objects
    course.category = None
    course.creator = None
    d = course.to_dict()
    assert d["category"] is None
    assert d["creator"] is None
