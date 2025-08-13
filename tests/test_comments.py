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

def test_add_comment(user_token, course_id):
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "Great course!"},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 200 or resp.status_code == 201
    data = resp.json()
    assert data["content"] == "Great course!"
    assert data["course_id"] == course_id

def test_list_comments(user_token, course_id):
    client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "Nice!"},
        headers=auth_headers(user_token)
    )
    resp = client.get(f"{API_PREFIX}/courses/{course_id}/comments/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(comment["content"] == "Nice!" for comment in data)

def test_edit_comment(user_token, course_id):
    # Add comment
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "Original comment"},
        headers=auth_headers(user_token)
    )
    comment_id = resp.json()["id"]
    # Edit comment
    resp = client.put(
        f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}",
        json={"content": "Edited comment"},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 200
    assert resp.json()["content"] == "Edited comment"

def test_delete_comment(user_token, course_id):
    # Add comment
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "To be deleted"},
        headers=auth_headers(user_token)
    )
    comment_id = resp.json()["id"]
    # Delete comment
    resp = client.delete(f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Comment deleted successfully"

def test_add_comment_unauthenticated(course_id):
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "Unauthenticated comment"}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"

def test_edit_comment_unauthenticated(user_token, course_id):
    # Add comment first
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "To edit"},
        headers=auth_headers(user_token)
    )
    comment_id = resp.json()["id"]
    # Try to edit without auth
    resp = client.put(
        f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}",
        json={"content": "Edited without auth"}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"

def test_delete_comment_unauthenticated(user_token, course_id):
    # Add comment first
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "To delete"},
        headers=auth_headers(user_token)
    )
    comment_id = resp.json()["id"]
    # Try to delete without auth
    resp = client.delete(f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"

def test_add_comment_nonexistent_course(user_token):
    resp = client.post(
        f"{API_PREFIX}/courses/999999/comments/",
        json={"content": "Comment on nonexistent course"},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Course not found"

def test_edit_nonexistent_comment(user_token, course_id):
    resp = client.put(
        f"{API_PREFIX}/courses/{course_id}/comments/999999",
        json={"content": "Edited nonexistent comment"},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Comment not found"

def test_delete_nonexistent_comment(user_token, course_id):
    resp = client.delete(f"{API_PREFIX}/courses/{course_id}/comments/999999", headers=auth_headers(user_token))
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Comment not found"

def test_edit_comment_forbidden(user_token, course_id):
    # Add comment as user
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "User's comment"},
        headers=auth_headers(user_token)
    )
    comment_id = resp.json()["id"]
    
    # Try to edit as another user (forbidden)
    another_user_token = unique_name("another_user")
    client.post(f"{API_PREFIX}/auth/register", json={"username": another_user_token, "password": "testpass"})
    another_user_resp = client.post(f"{API_PREFIX}/auth/login", json={"username": another_user_token, "password": "testpass"})

    resp = client.put(
        f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}",
        json={"content": "Edited by another user"},
        headers=auth_headers(another_user_resp.json()["access_token"])
    )
    
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not allowed to edit this comment"

def test_delete_comment_forbidden(user_token, course_id):
    # Add comment as user
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "User's comment"},
        headers=auth_headers(user_token)
    )
    comment_id = resp.json()["id"]
    
    # Try to delete as another user (forbidden)
    another_user_token = unique_name("another_user")
    client.post(f"{API_PREFIX}/auth/register", json={"username": another_user_token, "password": "testpass"})
    another_user_resp = client.post(f"{API_PREFIX}/auth/login", json={"username": another_user_token, "password": "testpass"})

    resp = client.delete(
        f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}",
        headers=auth_headers(another_user_resp.json()["access_token"])
    )
    
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not allowed to delete this comment"
