import pytest
import uuid
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_PREFIX = "/api/v1"


def unique_name(prefix="Category"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def user_token():
    username = unique_name("user")
    password = "testpass"
    client.post(f"{API_PREFIX}/auth/register", json={"username": username, "password": password})
    resp = client.post(f"{API_PREFIX}/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_category(user_token):
    name = unique_name("UniqueCategory")
    response = client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["name"] == name
    assert "id" in data


def test_create_category_unauthenticated():
    name = unique_name("NoAuthCategory")
    response = client.post(f"{API_PREFIX}/categories/", json={"name": name})
    assert response.status_code == 401


def test_create_duplicate_category(user_token):
    name = unique_name("DuplicateCategory")
    client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    response = client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    assert response.status_code == 400
    assert response.json()["detail"] == "Category with this name already exists."


def test_create_category_missing_name(user_token):
    response = client.post(f"{API_PREFIX}/categories/", json={}, headers=auth_headers(user_token))
    assert response.status_code == 422


def test_update_category(user_token):
    name = unique_name("ToUpdate")
    response = client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    category_id = response.json()["id"]
    new_name = unique_name("UpdatedName")
    response = client.put(f"{API_PREFIX}/categories/{category_id}", json={"name": new_name},
                          headers=auth_headers(user_token))
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name


def test_update_category_unauthenticated(user_token):
    name = unique_name("ToUpdateNoAuth")
    response = client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    category_id = response.json()["id"]
    response = client.put(f"{API_PREFIX}/categories/{category_id}", json={"name": unique_name("NoAuth")})
    assert response.status_code == 401


def test_update_category_duplicate_name(user_token):
    name1 = unique_name("FirstCategory")
    name2 = unique_name("SecondCategory")
    resp1 = client.post(f"{API_PREFIX}/categories/", json={"name": name1}, headers=auth_headers(user_token))
    resp2 = client.post(f"{API_PREFIX}/categories/", json={"name": name2}, headers=auth_headers(user_token))
    id2 = resp2.json()["id"]
    response = client.put(f"{API_PREFIX}/categories/{id2}", json={"name": name1}, headers=auth_headers(user_token))
    assert response.status_code == 400
    assert response.json()["detail"] == "Category with this name already exists."


def test_update_nonexistent_category(user_token):
    response = client.put(f"{API_PREFIX}/categories/999999", json={"name": unique_name("Nonexistent")},
                          headers=auth_headers(user_token))
    assert response.status_code == 404


def test_get_single_category(user_token):
    name = unique_name("SingleRetrieve")
    response = client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    category_id = response.json()["id"]
    response = client.get(f"{API_PREFIX}/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == name


def test_get_nonexistent_category():
    response = client.get(f"{API_PREFIX}/categories/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_delete_category(user_token):
    name = unique_name("ToDelete")
    response = client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    category_id = response.json()["id"]
    response = client.delete(f"{API_PREFIX}/categories/{category_id}", headers=auth_headers(user_token))
    assert response.status_code == 200
    assert response.json()["detail"] == "Category deleted"


def test_delete_category_unauthenticated(user_token):
    name = unique_name("ToDeleteNoAuth")
    response = client.post(f"{API_PREFIX}/categories/", json={"name": name}, headers=auth_headers(user_token))
    category_id = response.json()["id"]
    response = client.delete(f"{API_PREFIX}/categories/{category_id}")
    assert response.status_code == 401


def test_delete_nonexistent_category(user_token):
    response = client.delete(f"{API_PREFIX}/categories/999999", headers=auth_headers(user_token))
    assert response.status_code == 404
