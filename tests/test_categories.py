from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def unique_name(prefix="Category"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def test_create_category():
    name = unique_name("UniqueCategory")
    response = client.post("/api/categories/", json={"name": name})
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["name"] == name
    assert "id" in data

def test_create_duplicate_category():
    name = unique_name("DuplicateCategory")
    client.post("/api/categories/", json={"name": name})
    response = client.post("/api/categories/", json={"name": name})
    assert response.status_code == 400
    assert response.json()["detail"] == "Category with this name already exists."

def test_update_category():
    name = unique_name("ToUpdate")
    response = client.post("/api/categories/", json={"name": name})
    category_id = response.json()["id"]
    new_name = unique_name("UpdatedName")
    response = client.put(f"/api/categories/{category_id}", json={"name": new_name})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name

def test_update_category_duplicate_name():
    name1 = unique_name("FirstCategory")
    name2 = unique_name("SecondCategory")
    resp1 = client.post("/api/categories/", json={"name": name1})
    resp2 = client.post("/api/categories/", json={"name": name2})
    id2 = resp2.json()["id"]
    # Try to update the second to have the same name as the first
    response = client.put(f"/api/categories/{id2}", json={"name": name1})
    assert response.status_code == 400
    assert response.json()["detail"] == "Category with this name already exists."

def test_get_single_category():
    name = unique_name("SingleRetrieve")
    response = client.post("/api/categories/", json={"name": name})
    category_id = response.json()["id"]
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == name

def test_get_nonexistent_category():
    response = client.get("/api/categories/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
