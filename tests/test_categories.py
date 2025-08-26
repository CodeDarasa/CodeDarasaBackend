"""Test cases for category management in a FastAPI application."""
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_PREFIX = "/api/v1"


def unique_name(prefix="Category"):
    """Generate a unique name with a given prefix for testing purposes."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def unique_description(prefix="Description"):
    """Generate a unique description with a given prefix for testing purposes."""
    return f"{prefix} {uuid.uuid4().hex[:8]}"


def unique_youtube_url():
    """Generate a unique YouTube URL for testing purposes."""
    return f"https://youtu.be/{uuid.uuid4().hex[:11]}"


@pytest.fixture
def user_token():
    """Fixture to create a user and return an authentication token."""
    username = unique_name("user")
    password = "testpass"
    client.post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    resp = client\
        .post(f"{API_PREFIX}/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]


def auth_headers(token):
    """Generate authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {token}"}


def test_create_category(user_token):
    """Test creating a new category with a unique name and description."""
    name = unique_name("UniqueCategory")
    description = unique_description("UniqueCategory description")
    response = client\
        .post(f"{API_PREFIX}/categories/", json={"name": name, "description": description},
              headers=auth_headers(user_token))
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["name"] == name
    assert data.get("description") == description
    assert "id" in data


def test_create_category_unauthenticated():
    """Test creating a category without authentication."""
    name = unique_name("NoAuthCategory")
    description = unique_description("NoAuthCategory description")
    response = client.post(f"{API_PREFIX}/categories/", json={"name": name, "description": description})
    assert response.status_code == 401


def test_create_duplicate_category(user_token):
    """ Test creating a category with a duplicate name."""
    name = unique_name("DuplicateCategory")
    client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    response = client\
        .post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    assert response.status_code == 400
    assert response.json()["detail"] == "Category with this name already exists."


def test_create_category_missing_name(user_token):
    """Test creating a category without providing a name."""
    response = client.post(f"{API_PREFIX}/categories/", json={}, headers=auth_headers(user_token))
    assert response.status_code == 422


def test_update_category(user_token):
    """Test updating an existing category's name and description."""
    name = unique_name("ToUpdate")
    description = unique_description("Initial description")
    response = client\
        .post(f"{API_PREFIX}/categories/", json={"name": name, "description": description},
              headers=auth_headers(user_token))
    category_id = response.json()["id"]
    new_name = unique_name("UpdatedName")
    new_description = unique_description("Updated description")
    response = client.put(
        f"{API_PREFIX}/categories/{category_id}",
        json={"name": new_name, "description": new_description},
        headers=auth_headers(user_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name
    assert data.get("description") == new_description


def test_update_category_unauthenticated(user_token):
    """Test updating a category without authentication."""
    name = unique_name("ToUpdateNoAuth")
    description = unique_description("NoAuth initial description")
    response = client\
        .post(f"{API_PREFIX}/categories/", json={"name": name, "description": description},
              headers=auth_headers(user_token))
    category_id = response.json()["id"]
    response = client\
        .put(f"{API_PREFIX}/categories/{category_id}",
             json={"name": unique_name("NoAuth"), "description": unique_description("NoAuth desc")})
    assert response.status_code == 401


def test_update_category_duplicate_name(user_token):
    """Test updating a category to a name that already exists."""
    name1 = unique_name("FirstCategory")
    name2 = unique_name("SecondCategory")
    desc1 = unique_description("FirstCategory description")
    desc2 = unique_description("SecondCategory description")
    resp1 = client\
        .post(f"{API_PREFIX}/categories/", json={"name": name1, "description": desc1},
              headers=auth_headers(user_token))
    resp2 = client\
        .post(f"{API_PREFIX}/categories/", json={"name": name2, "description": desc2},
              headers=auth_headers(user_token))
    id2 = resp2.json()["id"]
    response = client\
        .put(
        f"{API_PREFIX}/categories/{id2}",
        json={"name": name1, "description": unique_description("Doesn't matter")},
        headers=auth_headers(user_token))
    assert response.status_code == 400
    assert response.json()["detail"] == "Category with this name already exists."


def test_update_nonexistent_category(user_token):
    """Test updating a category that does not exist."""
    response = client\
        .put(f"{API_PREFIX}/categories/999999",
             json={"name": unique_name("Nonexistent"), "description": unique_description("Nonexistent")},
             headers=auth_headers(user_token))
    assert response.status_code == 404


def test_get_single_category(user_token):
    """Test retrieving a single category by ID, including description and course details."""
    name = unique_name("SingleRetrieve")
    description = unique_description("SingleRetrieve description")
    response = client\
        .post(f"{API_PREFIX}/categories/", json={"name": name, "description": description},
              headers=auth_headers(user_token))
    category_id = response.json()["id"]
    response = client.get(f"{API_PREFIX}/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == name
    assert data.get("description") == description
    assert "courses" in data and isinstance(data["courses"], list)


def test_get_nonexistent_category():
    """Test retrieving a category that does not exist."""
    response = client.get(f"{API_PREFIX}/categories/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_create_course_with_nonexistent_category(user_token):
    """Test creating a course with a non-existent category should return 404."""
    title = unique_name("CourseTitle")
    description = unique_description("Course description")
    youtube_url = unique_youtube_url()
    payload = {
        "title": title,
        "description": description,
        "youtube_url": youtube_url,
        "category_id": 999999,
    }
    response = client.post(
        f"{API_PREFIX}/courses/",
        json=payload,
        headers=auth_headers(user_token),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_delete_category(user_token):
    """Test deleting an existing category."""
    name = unique_name("ToDelete")
    response = client\
        .post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    category_id = response.json()["id"]
    response = client\
        .delete(f"{API_PREFIX}/categories/{category_id}", headers=auth_headers(user_token))
    assert response.status_code == 200
    assert response.json()["detail"] == "Category deleted"


def test_delete_category_unauthenticated(user_token):
    """Test deleting a category without authentication."""
    name = unique_name("ToDeleteNoAuth")
    description = unique_description("ToDeleteNoAuth description")
    response = client\
        .post(f"{API_PREFIX}/categories/", json={"name": name, "description": description},
              headers=auth_headers(user_token))
    category_id = response.json()["id"]
    response = client.delete(f"{API_PREFIX}/categories/{category_id}")
    assert response.status_code == 401


def test_delete_nonexistent_category(user_token):
    """Test deleting a category that does not exist."""
    response = client.delete(f"{API_PREFIX}/categories/999999", headers=auth_headers(user_token))
    assert response.status_code == 404


def test_list_categories(user_token):
    """Test listing all categories."""
    # Create two categories
    name1 = unique_name("ListCat1")
    name2 = unique_name("ListCat2")
    client.post(f"{API_PREFIX}/categories/", json={"name": name1}, headers=auth_headers(user_token))
    client.post(f"{API_PREFIX}/categories/", json={"name": name2}, headers=auth_headers(user_token))
    response = client.get(f"{API_PREFIX}/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [cat["name"] for cat in data]
    assert name1 in names
    assert name2 in names


def test_create_category_with_courses(user_token):
    """Test creating a category and assigning courses to it."""
    # Create two courses
    course_payload1 = {
        "title": unique_name("CourseA"),
        "description": unique_description("CourseA desc"),
        "youtube_url": unique_youtube_url(),
    }
    course_payload2 = {
        "title": unique_name("CourseB"),
        "description": unique_description("CourseB desc"),
        "youtube_url": unique_youtube_url(),
    }
    resp1 = client.post(f"{API_PREFIX}/courses/", json=course_payload1, headers=auth_headers(user_token))
    resp2 = client.post(f"{API_PREFIX}/courses/", json=course_payload2, headers=auth_headers(user_token))
    course_id1 = resp1.json()["id"]
    course_id2 = resp2.json()["id"]

    # Create category with these courses
    cat_name = unique_name("CatWithCourses")
    response = client.post(
        f"{API_PREFIX}/categories/",
        json={"name": cat_name, "course_ids": [course_id1, course_id2]},
        headers=auth_headers(user_token)
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["name"] == cat_name
    # The category should list the courses
    course_ids_in_cat = [c["id"] for c in data.get("courses", [])]
    assert course_id1 in course_ids_in_cat
    assert course_id2 in course_ids_in_cat


def test_update_category_add_and_remove_courses(user_token):
    """Test adding and removing courses from a category during update."""
    # Create a category
    cat_name = unique_name("EditCat")
    cat_resp = client.post(
        f"{API_PREFIX}/categories/",
        json={"name": cat_name},
        headers=auth_headers(user_token)
    )
    category_id = cat_resp.json()["id"]

    # Create two courses
    course_payload1 = {
        "title": unique_name("EditCourseA"),
        "description": unique_description("EditCourseA desc"),
        "youtube_url": unique_youtube_url(),
    }
    course_payload2 = {
        "title": unique_name("EditCourseB"),
        "description": unique_description("EditCourseB desc"),
        "youtube_url": unique_youtube_url(),
    }
    resp1 = client.post(f"{API_PREFIX}/courses/", json=course_payload1, headers=auth_headers(user_token))
    resp2 = client.post(f"{API_PREFIX}/courses/", json=course_payload2, headers=auth_headers(user_token))
    course_id1 = resp1.json()["id"]
    course_id2 = resp2.json()["id"]

    # Add both courses to the category
    response = client.put(
        f"{API_PREFIX}/categories/{category_id}",
        json={"add_course_ids": [course_id1, course_id2]},
        headers=auth_headers(user_token)
    )
    assert response.status_code == 200
    data = response.json()
    course_ids_in_cat = [c["id"] for c in data.get("courses", [])]
    assert course_id1 in course_ids_in_cat
    assert course_id2 in course_ids_in_cat

    # Remove one course from the category
    response = client.put(
        f"{API_PREFIX}/categories/{category_id}",
        json={"remove_course_ids": [course_id1]},
        headers=auth_headers(user_token)
    )
    assert response.status_code == 200
    data = response.json()
    course_ids_in_cat = [c["id"] for c in data.get("courses", [])]
    assert course_id1 not in course_ids_in_cat
