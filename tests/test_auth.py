from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def unique_username():
    return f"user_{uuid.uuid4().hex[:8]}"

def test_register_and_login():
    username = unique_username()
    password = "testpass"
    # Register
    resp = client.post("/api/auth/register", json={"username": username, "password": password})
    assert resp.status_code in (200, 201)
    # Login
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

def test_profile_update():
    username = unique_username()
    password = "testpass"
    # Register and login
    client.post("/api/auth/register", json={"username": username, "password": password})
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    print(resp.json())
    token = resp.json()["access_token"]
    # Update profile
    resp = client.put(
        "/api/users/me",
        json={"username": "newusername", "full_name": "Jane Doe", "bio": "Test bio"},
        headers={"Authorization": f"Bearer {token}"}
    )
    print(resp.json())
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Jane Doe"
    assert data["bio"] == "Test bio"
