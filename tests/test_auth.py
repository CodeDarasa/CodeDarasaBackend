from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.course import Course
import uuid

client = TestClient(app)

def test_register_and_login():
     # Generate a unique username and course title
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    course_title = f"Protected Course {uuid.uuid4().hex[:8]}"

    # Clean up any old test users/courses with the same username/title
    db = SessionLocal()
    db.query(User).filter(User.username == username).delete()
    db.query(Course).filter(Course.title == course_title).delete()
    db.commit()
    db.close()
    
    # Register a new user
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username

    # Login with the new user
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]

    # Use the token to create a course (protected endpoint)
    response = client.post(
        "/api/courses/",
        json={
            "title": course_title,
            "description": "Should only work if authenticated.",
            "youtube_url": "https://youtube.com/protected"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    course = response.json()
    assert course["title"] == course_title
