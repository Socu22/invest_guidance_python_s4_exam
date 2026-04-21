from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)


def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_single_item():
    response = client.get("/items/1")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Item 1"


def test_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 200

    data = response.json()
    assert "error" in data