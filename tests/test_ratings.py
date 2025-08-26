"""Test cases for course ratings functionality in the FastAPI application."""
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


def auth_headers(token):
    """Generate authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {token}"}


def test_rate_course(user_token, course_id):
    """Test rating a course with valid data."""
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 5},
        headers=auth_headers(user_token)
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["value"] == 5
    assert data["course_id"] == course_id


def test_list_course_ratings(user_token, course_id):
    """Test listing ratings for a course."""
    client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 4},
        headers=auth_headers(user_token)
    )
    resp = client.get(f"{API_PREFIX}/courses/{course_id}/ratings/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(rating["value"] == 4 for rating in data)


def test_delete_rating(user_token, course_id):
    """Test deleting a rating for a course."""
    # Add rating
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 2},
        headers=auth_headers(user_token)
    )
    rating_id = resp.json()["id"]
    # Delete rating
    resp = client\
        .delete(
        f"{API_PREFIX}/courses/{course_id}/ratings/{rating_id}", headers=auth_headers(user_token)
    )
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Rating deleted successfully"


def test_rate_course_unauthenticated(course_id):
    """Test rating a course without authentication."""
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 5}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"


def test_delete_rating_unauthenticated(user_token, course_id):
    """Test deleting a rating without authentication."""
    # Add rating first
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 2},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 200
    rating_id = resp.json()["id"]
    # Try to delete without auth
    resp = client.delete(f"{API_PREFIX}/courses/{course_id}/ratings/{rating_id}")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"


def test_rate_nonexistent_course(user_token):
    """Test rating a course that does not exist."""
    resp = client.post(
        f"{API_PREFIX}/courses/999999/ratings/",
        json={"value": 5},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Course not found"


def test_delete_nonexistent_rating(user_token, course_id):
    """Test deleting a rating that does not exist."""
    resp = client\
        .delete(
        f"{API_PREFIX}/courses/{course_id}/ratings/999999", headers=auth_headers(user_token)
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Rating not found"


def test_delete_rating_forbidden(user_token, course_id):
    """Test deleting a rating as a different user."""
    # Add rating as user
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 3},
        headers=auth_headers(user_token)
    )
    rating_id = resp.json()["id"]

    # Try to delete as another user (forbidden)
    another_user_token = unique_name("another_user")
    client\
        .post(
        f"{API_PREFIX}/auth/register", json={"username": another_user_token, "password": "testpass"}
    )
    another_user_resp = client.post(f"{API_PREFIX}/auth/login",
                                    json={"username": another_user_token, "password": "testpass"})

    resp = client.delete(
        f"{API_PREFIX}/courses/{course_id}/ratings/{rating_id}",
        headers=auth_headers(another_user_resp.json()["access_token"])
    )

    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not allowed to delete this rating"


def test_rate_course_update_existing(user_token, course_id):
    """Test rating a course that you have already rated updates the rating."""
    # First rating
    resp1 = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 3},
        headers=auth_headers(user_token)
    )
    assert resp1.status_code in (200, 201)
    data1 = resp1.json()
    assert data1["value"] == 3

    # Rate again with a different value
    resp2 = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 5},
        headers=auth_headers(user_token)
    )
    assert resp2.status_code in (200, 201)
    data2 = resp2.json()
    assert data2["value"] == 5
    assert data2["id"] == data1["id"]  # Should update the same rating, not create a new one


def test_get_single_rating(user_token, course_id):
    """Test retrieving a specific rating by ID."""
    # Rate the course
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 4},
        headers=auth_headers(user_token)
    )
    assert resp.status_code in (200, 201)
    rating_id = resp.json()["id"]

    # Retrieve all ratings for the course and check the specific rating is present
    resp_all = client.get(f"{API_PREFIX}/courses/{course_id}/ratings/")
    assert resp_all.status_code == 200
    ratings = resp_all.json()
    assert any(r["id"] == rating_id for r in ratings)


def test_get_all_ratings_for_user(user_token, course_id):
    """Test retrieving all ratings made by the current user."""
    # Rate the course
    client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 5},
        headers=auth_headers(user_token)
    )
    # Retrieve all ratings for the user
    resp = client.get(f"{API_PREFIX}/users/me/ratings/", headers=auth_headers(user_token))
    assert resp.status_code == 200
    ratings = resp.json()
    assert isinstance(ratings, list)
    assert any(r["course_id"] == course_id for r in ratings)


def test_rating_get_id_and_to_dict():
    """Test the get_id and to_dict methods of the Rating model."""
    from app.db.models.rating import Rating

    rating = Rating(
        id=55,
        value=4,
        user_id=10,
        course_id=20
    )

    # Test get_id
    assert rating.get_id() == 55

    # Test to_dict
    d = rating.to_dict()
    assert isinstance(d, dict)
    assert d["id"] == 55
    assert d["value"] == 4
    assert d["user_id"] == 10


def test_userrole_get_id():
    """Test the get_id method of the User model."""
    from app.db.models.user import User
    user = User(id=123, username="testuser")
    assert user.get_id() == 123
