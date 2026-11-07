import pytest
from fastapi.testclient import TestClient

from main import app, inventory

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_inventory():
    inventory.clear()
    yield
    inventory.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_add_item():
    response = client.post("/items", json={"name": "item1", "price": 10.0, "stock": 5})
    assert response.status_code == 201
    assert response.json() == {"name": "item1", "price": 10.0, "stock": 5}

def test_add_existing_item():
    client.post("/items", json={"name": "item1", "price": 10.0, "stock": 5})
    response = client.post("/items", json={"name": "item1", "price": 15.0, "stock": 3})
    assert response.status_code == 409
    assert response.json() == {"detail": "Item 'item1' already exists"}
    stored = client.get("/items/item1")
    assert stored.json()["price"] == 10.0
    assert stored.json()["stock"] == 5

def test_add_item_negative_stock_returns_422():
    response = client.post("/items", json={"name": "item1", "price": 10.0, "stock": -5})
    assert response.status_code == 422

def test_invalid_price():
    response = client.post("/items", json={"name": "item1", "price": "abc", "stock": 5})
    assert response.status_code == 422

def test_existing_item():
    client.post("/items", json={"name": "item1", "price": 10.0, "stock": 4})
    response = client.get("/items/item1")
    assert response.status_code == 200
    assert response.json() == {"name": "item1", "price": 10.0, "stock": 4}

def test_get_missing_item():
    response = client.get("/items/none")
    assert response.status_code == 404

def test_reduce_stock():
    client.post("/items", json={"name": "item1", "price": 10.0, "stock": 7})
    response = client.patch("/items/item1", json={"change": -3})
    assert response.status_code == 200
    assert response.json()["stock"] == 4


def test_too_much_reduction():
    client.post("/items", json={"name": "item1", "price": 10.0, "stock": 5})
    response = client.patch("/items/item1", json={"change": -10})
    assert response.status_code == 409
    stored = client.get("/items/item1")
    assert stored.json()["stock"]== 5

def test_missing_item_update_stock():
    response = client.patch("/items/none", json={"change": 5})
    assert response.status_code == 404

def test_invalid_change():
    client.post("/items", json={"name": "item1", "price": 10.0, "stock": 5})
    response = client.patch("/items/item1", json= {"change": "abc"})
    assert response.status_code == 422

def test_sale_success():
    client.post("/items", json= {"name": "item1", "price": 10.0, "stock": 5})
    client.post("/items", json= {"name": "item2", "price": 20.0, "stock": 3})
    response = client.post("/sales", json= {"items": {"item1": 2, "item2": 1}})
    assert response.status_code == 200
    assert response.json() == {"total_revenue": 40.0}

def test_sale_reduce_stock():
    client.post("/items", json= {"name": "item1", "price": 10.0, "stock": 5})
    client.post("/items", json= {"name": "item2", "price": 20.0, "stock": 3})
    response = client.post("/sales", json= {"items": {"item1": 2, "item2": 1}})
    assert response.status_code == 200
    store = client.get("/items/item1")
    store2 = client.get("/items/item2")
    assert store.json()["stock"] == 3
    assert store2.json()["stock"] == 2

def test_sale_missing_item():
    client.post("/items", json= {"name": "item1", "price": 10.0, "stock": 5})
    response = client.post("/sales", json= {"items": {"item1": 2, "item2": 1}})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item 'item2' not found!"}
    stored = client.get ("/items/item1")
    assert stored.json()["stock"] == 5

def test_sale_insufficient_stock():
    client.post("/items", json= {"name": "item1", "price": 10.0, "stock": 5})
    response = client.post("/sales", json= {"items": {"item1": 10}})
    assert response.status_code == 409
    assert response.json() == {"detail": "Not enough stock for item 'item1'"}
    stored = client.get("/items/item1")
    assert stored.json()["stock"] == 5

def test_sale_invalid_quantity():
    client.post("/items", json= {"name": "item1", "price": 10.0, "stock": 5})
    response = client.post("/sales", json= {"items": {"item1": "abc"}})
    assert response.status_code == 422
    stored = client.get("/items/item1")
    assert stored.json()["stock"] == 5

def test_sale_negative_quantity():
    client.post("/items", json= {"name": "item1", "price": 10.0, "stock": 5})
    response = client.post("/sales", json= {"items": {"item1": -2}})
    assert response.status_code == 422
    stored = client.get("/items/item1")
    assert stored.json()["stock"] == 5

def test_existing_name_with_different_price():
    client.post("/items", json= {"name": "item1", "price": 10.0, "stock": 5})
    response = client.post("/items", json= {"name": "item1", "price": 15.0, "stock": 3})
    assert response.status_code == 409
    assert response.json() == {"detail": "Item 'item1' already exists"}
    stored = client.get("/items/item1")
    assert stored.json()["price"] == 10.0
    assert stored.json()["stock"] == 5