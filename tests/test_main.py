# test_main.py
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app, Base, Product  # Assurez-vous d'importer Product depuis main
from pydantic import BaseModel

# Définition de l'URL de la base de données de test SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_product.db"

# Configuration de la base de données de test
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création des tables de la base de données de test
Base.metadata.create_all(bind=engine)

# Modèle Pydantic pour la création de produit
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float

@pytest.fixture(scope="function")
def test_db_session():
    """
    Fixture pour créer une session de base de données propre pour chaque fonction de test.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# def test_read_products(test_db_session):
#     # Supprimer toutes les données existantes de la table "products" avant de créer de nouveaux produits
#     test_db_session.execute(text("DELETE FROM products"))

#     # Vérifier que les données sont bien supprimées
#     assert test_db_session.query(Product).count() == 0

#     # Créer quelques produits de test dans la base de données de test
#     products_to_create = [
#         {"name": "Product 1", "description": "Description 1", "price": 49.99},
#         {"name": "Product 2", "description": "Description 2", "price": 59.99},
#     ]
#     with TestClient(app) as client:
#         for product_data in products_to_create:
#             product_create = ProductCreate(**product_data)
#             response = client.post("/products/", json=product_create.dict())

#     # Appel à l'API pour récupérer tous les produits après la création
#     with TestClient(app) as client:
#         response = client.get("/products/")

#         # Vérifier que la requête a réussi (code de statut 200 OK)
#         assert response.status_code == 200
#         products = response.json()
#         assert len(products) == 2  # On s'attend à trouver exactement 2 produits après la création
def test_create_product(test_db_session):
    # Données de test pour créer un produit
    product_data = {
        "name": "Test Product",
        "description": "Test description",
        "price": 99.99
    }

    # Appel à l'API pour créer le produit
    with TestClient(app) as client:
        response = client.post("/products/", json=product_data)

        # Vérifier que la création a réussi (code de statut 201 Created)
        assert response.status_code == 201
        created_product = response.json()
        assert created_product["name"] == product_data["name"]
        assert created_product["description"] == product_data["description"]
        assert created_product["price"] == product_data["price"]
def test_update_product(test_db_session):
    # Créer un produit de test dans la base de données de test
    product_data = {
        "name": "Product to Update",
        "description": "Old description",
        "price": 99.99
    }
    with TestClient(app) as client:
        response = client.post("/products/", json=product_data)
        created_product = response.json()

    # Données mises à jour pour le produit
    updated_product_data = {
        "name": "Updated Product",
        "description": "New description",
        "price": 119.99
    }

    # Appel à l'API pour mettre à jour le produit
    with TestClient(app) as client:
        response = client.put(f"/products/{created_product['id']}", json=updated_product_data)

        # Vérifier que la mise à jour a réussi (code de statut 200 OK)
        assert response.status_code == 200

        # Vérifier que les données du produit mis à jour correspondent aux données mises à jour
        updated_product = response.json()
        assert updated_product["name"] == updated_product_data["name"]
        assert updated_product["description"] == updated_product_data["description"]
        assert updated_product["price"] == updated_product_data["price"]

def test_delete_product(test_db_session):
    # Créer un produit de test dans la base de données de test
    product_data = {
        "name": "Product to Delete",
        "description": "To be deleted",
        "price": 129.99
    }
    with TestClient(app) as client:
        response = client.post("/products/", json=product_data)
        created_product = response.json()

    # Appel à l'API pour supprimer le produit par son ID
    with TestClient(app) as client:
        response = client.delete(f"/products/{created_product['id']}")

        # Vérifier que la suppression a réussi (code de statut 200 OK)
        assert response.status_code == 200
        assert response.json() == {"message": "Product deleted"}

if __name__ == "__main__":
    pytest.main()
