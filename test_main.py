import pytest
from fastapi.testclient import TestClient
from main import app  # Replace `main` with the name of your FastAPI app file

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_item():
    payload = {
        "name": "Test Item",
        "description": "A sample test item",
        "price": 9.99,
        "quantity": 10,
        "is_registered": True
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 200
    assert "item" in response.json()

def test_get_item():
    # Create an item first
    payload = {
        "name": "Test Item",
        "description": "A sample test item",
        "price": 9.99,
        "quantity": 10,
        "is_registered": True
    }
    create_response = client.post("/items", json=payload)
    item_id = create_response.json()["item"]["id"]

    # Fetch the created item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]

def test_get_all_items():
    response = client.get("/items?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 5

def test_update_item():
    # Create an item first
    payload = {
        "name": "Old Item",
        "description": "Old description",
        "price": 10.0,
        "quantity": 5,
        "is_registered": True
    }
    create_response = client.post("/items", json=payload)
    item_id = create_response.json()["item"]["id"]

    # Update the item
    updated_payload = {
        "name": "Updated Item",
        "description": "Updated description",
        "price": 15.0,
        "quantity": 8,
        "is_registered": False
    }
    response = client.put(f"/items/{item_id}", json=updated_payload)
    assert response.status_code == 200
    assert response.json()["name"] == updated_payload["name"]

def test_delete_item():
    # Create an item first
    payload = {
        "name": "Item to delete",
        "description": "Delete this item",
        "price": 5.0,
        "quantity": 3,
        "is_registered": False
    }
    create_response = client.post("/items", json=payload)
    item_id = create_response.json()["item"]["id"]

    # Delete the item
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["item_id"] == item_id

    # Ensure the item no longer exists
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 404
