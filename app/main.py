# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select, Session
from app.db import create_schema_and_tables, get_session
from app.models import Product, ShoppingListItem
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class ItemInput(BaseModel):
    product_id: int
    quantity: int = 1

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_schema_and_tables()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)


# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],  # Puedes limitar si lo deseas: ["GET", "POST"]
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Shopping List API is running"}

@app.post("/products/", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@app.post("/products/bulk")
def create_products_bulk(products: list[Product], session: Session = Depends(get_session)):
    session.add_all(products)
    session.commit()
    return {"message": f"{len(products)} products added."}

@app.get("/products", response_model=list[Product])
def list_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return products

@app.post("/shopping-list")
def add_to_shopping_list(product_id: int, quantity: int = 1, session: Session = Depends(get_session)):
    # Verificamos que el producto existe
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Verificamos si el producto ya está en la lista para actualizar la cantidad
    existing_item = session.exec(
        select(ShoppingListItem).where(ShoppingListItem.product_id == product_id)
    ).first()

    if existing_item:
        existing_item.quantity += quantity
        session.add(existing_item)
        session.commit()
        session.refresh(existing_item)
        return existing_item

    # Si no existe, creamos nuevo item
    item = ShoppingListItem(product_id=product_id, quantity=quantity)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.post("/shopping-list/bulk")
def add_multiple_items(items: list[ItemInput], session: Session = Depends(get_session)):
    added_items = []

    for item in items:
        product = session.get(Product, item.product_id)
        if not product:
            continue  # O puedes levantar una excepción si prefieres

        existing_item = session.exec(
            select(ShoppingListItem).where(ShoppingListItem.product_id == item.product_id)
        ).first()

        if existing_item:
            existing_item.quantity += item.quantity
            session.add(existing_item)
            session.commit()
            session.refresh(existing_item)
            added_items.append(existing_item)
        else:
            new_item = ShoppingListItem(product_id=item.product_id, quantity=item.quantity)
            session.add(new_item)
            session.commit()
            session.refresh(new_item)
            added_items.append(new_item)

    return added_items

@app.get("/shopping-list")
def get_shopping_list(session: Session = Depends(get_session)):
    items = session.exec(select(ShoppingListItem)).all()
    return items


@app.delete("/shopping-list/{item_id}")
def delete_from_shopping_list(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ShoppingListItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    session.delete(item)
    session.commit()
    return {"ok": True}