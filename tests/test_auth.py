import uuid
from fastapi.testclient import TestClient
from app.main import app

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

def test_register_duplicate_username():
    username = unique_username()
    password = "testpass"
    client.post("/api/auth/register", json={"username": username, "password": password})
    resp = client.post("/api/auth/register", json={"username": username, "password": password})
    assert resp.status_code == 400 or resp.status_code == 409

def test_login_wrong_password():
    username = unique_username()
    password = "testpass"
    client.post("/api/auth/register", json={"username": username, "password": password})
    resp = client.post("/api/auth/login", json={"username": username, "password": "wrongpass"})
    assert resp.status_code == 401

def test_login_nonexistent_user():
    resp = client.post("/api/auth/login", json={"username": "nonexistent", "password": "nopass"})
    assert resp.status_code == 401

def test_profile_update():
    username = unique_username()
    password = "testpass"
    # Register and login
    client.post("/api/auth/register", json={"username": username, "password": password})
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    token = resp.json()["access_token"]
    # Update profile
    resp = client.put(
        "/api/users/me",
        json={"username": "newusername", "full_name": "Jane Doe", "bio": "Test bio"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Jane Doe"
    assert data["bio"] == "Test bio"

def test_profile_update_unauthenticated():
    resp = client.put(
        "/api/users/me",
        json={"full_name": "Jane Doe", "bio": "Test bio"}
    )
    assert resp.status_code == 401

def test_get_profile():
    username = unique_username()
    password = "testpass"
    client.post("/api/auth/register", json={"username": username, "password": password})
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    token = resp.json()["access_token"]
    resp = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == username

def test_get_profile_unauthenticated():
    resp = client.get("/api/users/me")
    assert resp.status_code == 401
