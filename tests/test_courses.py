import pytest
from fastapi.testclient import TestClient
from app.db.session import SessionLocal
from app.db.models.course import Course
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def clean_courses():
    db = SessionLocal()
    db.query(Course).delete()
    db.commit()
    db.close()

def test_create_course():
    response = client.post(
        "/api/courses/",
        json={
            "title": "Test Course Unique 1",
            "description": "A course for testing.",
            "youtube_url": "https://youtube.com/test1"
        }
    )
    print(response.status_code, response.json())
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Course Unique 1"
    assert data["description"] == "A course for testing."
    assert data["youtube_url"] == "https://youtube.com/test1"

def test_get_courses():
    response = client.get("/api/courses/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_single_course():
    # First, create a course
    create_resp = client.post(
        "/api/courses/",
        json={
            "title": "Unique Course 2",
            "description": "Single fetch test.",
            "youtube_url": "https://youtube.com/unique2"
        }
    )
    assert create_resp.status_code == 200 or create_resp.status_code == 201, create_resp.json()
    course_id = create_resp.json()["id"]
    # Now, fetch it
    response = client.get(f"/api/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == course_id

def test_update_course():
    # Create a course
    create_resp = client.post(
        "/api/courses/",
        json={
            "title": "Update Me 3",
            "description": "Before update.",
            "youtube_url": "https://youtube.com/updateme3"
        }
    )
    assert create_resp.status_code == 200 or create_resp.status_code == 201, create_resp.json()
    course_id = create_resp.json()["id"]
    # Update it
    response = client.put(
        f"/api/courses/{course_id}",
        json={
            "title": "Updated Title 3",
            "description": "After update.",
            "youtube_url": "https://youtube.com/updated3"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title 3"

def test_delete_course():
    # Create a course
    create_resp = client.post(
        "/api/courses/",
        json={
            "title": "Delete Me",
            "description": "To be deleted.",
            "youtube_url": "https://youtube.com/deleteme"
        }
    )
    course_id = create_resp.json()["id"]
    # Delete it
    response = client.delete(f"/api/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Course deleted successfully."
