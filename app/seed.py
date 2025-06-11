# app/seed.py
import json
from pathlib import Path
from sqlmodel import Session
from app.db import engine
from app.models import Product

DATA_PATH = Path(__file__).parent.parent / "data" / "items.json"

def load_products_from_json():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        products_data = json.load(file)
    with Session(engine) as session:
        for product in products_data:
            db_product = Product(**product)
            session.add(db_product)
        session.commit()
    print(f"{len(products_data)} products loaded into database.")

if __name__ == "__main__":
    load_products_from_json()