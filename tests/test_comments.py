"""Test cases for course comments API endpoints."""
import uuid
from datetime import datetime, timezone

import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.db.models.comment import Comment

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


def test_add_comment(user_token, course_id):
    """Test adding a comment to a course."""
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "Great course!"},
        headers=auth_headers(user_token)
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["content"] == "Great course!"
    assert data["course_id"] == course_id


def test_list_comments(user_token, course_id):
    """Test listing comments for a course."""
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
    """Test editing a comment on a course."""
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
    """Test deleting a comment from a course."""
    # Add comment
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "To be deleted"},
        headers=auth_headers(user_token)
    )
    comment_id = resp.json()["id"]
    # Delete comment
    resp = client\
        .delete(
        f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Comment deleted successfully"


def test_add_comment_unauthenticated(course_id):
    """Test adding a comment without authentication."""
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "Unauthenticated comment"}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"


def test_edit_comment_unauthenticated(user_token, course_id):
    """Test editing a comment without authentication."""
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
    """Test deleting a comment without authentication."""
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
    """Test adding a comment to a nonexistent course."""
    resp = client.post(
        f"{API_PREFIX}/courses/999999/comments/",
        json={"content": "Comment on nonexistent course"},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Course not found"


def test_edit_nonexistent_comment(user_token, course_id):
    """Test editing a nonexistent comment."""
    resp = client.put(
        f"{API_PREFIX}/courses/{course_id}/comments/999999",
        json={"content": "Edited nonexistent comment"},
        headers=auth_headers(user_token)
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Comment not found"


def test_delete_nonexistent_comment(user_token, course_id):
    """Test deleting a nonexistent comment."""
    resp = client\
        .delete(
        f"{API_PREFIX}/courses/{course_id}/comments/999999", headers=auth_headers(user_token))
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Comment not found"


def test_edit_comment_forbidden(user_token, course_id):
    """Test editing a comment as another user (forbidden)."""
    # Add comment as user
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "User's comment"},
        headers=auth_headers(user_token)
    )
    comment_id = resp.json()["id"]

    # Try to edit as another user (forbidden)
    another_user_token = unique_name("another_user")
    client\
        .post(
        f"{API_PREFIX}/auth/register", json={"username": another_user_token, "password": "testpass"}
    )
    another_user_resp = client.post(f"{API_PREFIX}/auth/login",
                                    json={"username": another_user_token, "password": "testpass"})

    resp = client.put(
        f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}",
        json={"content": "Edited by another user"},
        headers=auth_headers(another_user_resp.json()["access_token"])
    )

    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not allowed to edit this comment"


def test_delete_comment_forbidden(user_token, course_id):
    """Test deleting a comment as another user (forbidden)."""
    # Add comment as user
    resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": "User's comment"},
        headers=auth_headers(user_token)
    )
    comment_id = resp.json()["id"]

    # Try to delete as another user (forbidden)
    another_user_token = unique_name("another_user")
    client\
        .post(
        f"{API_PREFIX}/auth/register", json={"username": another_user_token, "password": "testpass"}
    )
    another_user_resp = client.post(f"{API_PREFIX}/auth/login",
                                    json={"username": another_user_token, "password": "testpass"})

    resp = client.delete(
        f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}",
        headers=auth_headers(another_user_resp.json()["access_token"])
    )

    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not allowed to delete this comment"


def test_get_comment(user_token, course_id):
    """Test retrieving a specific comment by ID."""
    # Add a comment first
    comment_content = "This is a test comment"
    add_resp = client.post(
        f"{API_PREFIX}/courses/{course_id}/comments/",
        json={"content": comment_content},
        headers=auth_headers(user_token)
    )
    assert add_resp.status_code == 200
    comment_id = add_resp.json()["id"]

    # Retrieve the comment
    get_resp = client.get(
        f"{API_PREFIX}/courses/{course_id}/comments/{comment_id}"
    )
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert isinstance(data, list)
    assert any(comment["id"] == comment_id and comment["content"] == comment_content for comment in data)


def test_comment_get_id_and_to_dict():
    """Test the get_id and to_dict methods of the Comment model."""

    # Create a Comment instance
    now = datetime.now(timezone.utc)
    comment = Comment(
        id=42,
        content="Test comment",
        created_at=now,
        user_id=7,
        course_id=3
    )

    # Test get_id
    assert comment.get_id() == 42

    # Test to_dict
    d = comment.to_dict()
    assert isinstance(d, dict)
    assert d["id"] == 42
    assert d["content"] == "Test comment"
    assert d["created_at"] == now.isoformat()
    assert d["user_id"] == 7
