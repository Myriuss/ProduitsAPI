from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, Product
from faker import Faker
import random

# Configuration de la base de données
SQLALCHEMY_DATABASE_URL = "sqlite:///./product.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialisation de Faker pour générer des données aléatoires
faker = Faker()

# Fonction pour remplir la base de données avec des produits de test
def fill_db(num_products: int):
    db = SessionLocal()
    try:
        for _ in range(num_products):
            product = Product(
                name=faker.word(),
                description=faker.sentence(),
                price=random.uniform(10.0, 100.0)
            )
            db.add(product)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    # Remplissage de la base de données avec 10 produits de test
    fill_db(10)
    print("Database filled with test data successfully!")
