import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

API_PREFIX = "/api/v1"

def unique_name(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def user_token():
    username = unique_name("user")
    password = "testpass"
    client.post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    resp = client.post(f"{API_PREFIX}/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]

@pytest.fixture
def category_id(user_token):
    name = unique_name("Category")
    resp = client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers={"Authorization": f"Bearer {user_token}"})
    return resp.json()["id"]

@pytest.fixture
def course_id(user_token, category_id):
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
    return {"Authorization": f"Bearer {token}"}

def test_rate_course(user_token, course_id):
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 5},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 200 or resp.status_code == 201
    data = resp.json()
    assert data["value"] == 5
    assert data["course_id"] == course_id

def test_list_course_ratings(user_token, course_id):
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
    # Add rating
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 2},
        headers=auth_headers(user_token)
    )
    rating_id = resp.json()["id"]
    # Delete rating
    resp = client.delete(f"{API_PREFIX}/courses/{course_id}/ratings/{rating_id}", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Rating deleted successfully"

def test_rate_course_unauthenticated(course_id):
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 5}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"

def test_delete_rating_unauthenticated(user_token, course_id):
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
    resp = client.post(
        f"{API_PREFIX}/courses/999999/ratings/",
        json={"value": 5},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Course not found"

def test_delete_nonexistent_rating(user_token, course_id):
    resp = client.delete(f"{API_PREFIX}/courses/{course_id}/ratings/999999", headers=auth_headers(user_token))
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Rating not found"

def test_delete_rating_forbidden(user_token, course_id):
    # Add rating as user
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/ratings/",
        json={"value": 3},
        headers=auth_headers(user_token)
    )
    rating_id = resp.json()["id"]
    
    # Try to delete as another user (forbidden)
    another_user_token = unique_name("another_user")
    client.post(f"{API_PREFIX}/auth/register", json={"username": another_user_token, "password": "testpass"})
    another_user_resp = client.post(f"{API_PREFIX}/auth/login", json={"username": another_user_token, "password": "testpass"})

    resp = client.delete(
        f"{API_PREFIX}/courses/{course_id}/ratings/{rating_id}",
        headers=auth_headers(another_user_resp.json()["access_token"])
    )
    
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not allowed to delete this rating"
