import pytest
from fastapi.testclient import TestClient
from main import app, get_db, create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, Product, User, SessionLocal, SQLALCHEMY_DATABASE_URL

# Override database to use a SQLite in-memory database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Function to override get_db to use TestingSessionLocal
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency override to use testing session
app.dependency_overrides[get_db] = override_get_db

# Fixture to create a TestClient instance for each test
@pytest.fixture
def client():
    return TestClient(app)

# Fixture to generate a valid access token for testing purposes
@pytest.fixture
def test_token():
    return create_access_token(data={"sub": "testuser"})

# Test cases
def test_create_user(client):
    response = client.post(
        "/users/",
        json={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["username"] == "testuser"
    assert "id" in created_user

def test_create_product(client, test_token):
    product_data = {"name": "Test Product", "description": "Test Description", "price": 99.99}
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.post("/products/", json=product_data, headers=headers)
    assert response.status_code == 201
    created_product = response.json()
    assert created_product["name"] == product_data["name"]
    assert created_product["description"] == product_data["description"]
    assert created_product["price"] == product_data["price"]
    assert "id" in created_product

def test_read_products(client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/products/", headers=headers)
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    for product in products:
        assert "id" in product
        assert "name" in product
        assert "description" in product
        assert "price" in product

def test_read_product(client, test_token):
    # Assuming there's at least one product in the database
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/products/", headers=headers)
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    product_id = products[0]["id"]
    response = client.get(f"/products/{product_id}", headers=headers)
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == product_id

def test_update_product(client, test_token):
    # 1. Fetch products to get a product ID for updating
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/products/", headers=headers)
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    product_id = products[0]["id"]

    # 2. Prepare updated data
    updated_data = {
        "name": "Updated Product Name",
        "description": "Updated Description",  # Add description field
        "price": 19.99  # Add price field
    }

    # 3. Make PUT request to update the product
    response = client.put(f"/products/{product_id}", json=updated_data, headers=headers)

    # 4. Check the response status code
    if response.status_code != 200:
        print(response.json())  # Print the response body for debugging
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    # 5. Optionally, verify the updated product details
    updated_product = response.json()
    assert updated_product["id"] == product_id
    assert updated_product["name"] == updated_data["name"]
    assert updated_product["description"] == updated_data["description"]
    assert updated_product["price"] == updated_data["price"]



def test_delete_product(client, test_token):
    # Assuming there's at least one product in the database
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/products/", headers=headers)
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    product_id = products[0]["id"]
    response = client.delete(f"/products/{product_id}", headers=headers)
    assert response.status_code == 200
    deletion_result = response.json()
    assert "message" in deletion_result
    assert deletion_result["message"] == "Product deleted"
