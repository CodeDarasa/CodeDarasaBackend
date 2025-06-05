from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_category():
    response = client.post(
        "/api/categories/",
        json={"name": "Test Category"}
    )
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Category"
    assert "id" in data

def test_list_categories():
    # Ensure at least one category exists
    client.post("/api/categories/", json={"name": "Another Category"})
    response = client.get("/api/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(cat["name"] == "Test Category" for cat in data)
