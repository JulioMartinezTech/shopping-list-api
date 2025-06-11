from  sqlmodel import SQLModel, Field, Relationship

SCHEMA= "shopping"

# ---------- PRODUCT MODEL (Catálogo) ----------
class Product(SQLModel, table=True):
    __table_args__ = {"schema": SCHEMA}

    id: int = Field(default=None, primary_key=True)
    name: str
    price: float
    image_url: str = None

    # Relación inversa: productos en listas
    shopping_list_items: list["ShoppingListItem"] = Relationship(back_populates="product")


# ---------- SHOPPING LIST ITEM (Relación con cantidad) ----------
class ShoppingListItem(SQLModel, table=True):
    __table_args__ = {"schema": SCHEMA}

    id: int = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key=f"{SCHEMA}.product.id")
    quantity: int = Field(default=1)

    # Relaciones
    product: Product = Relationship(back_populates="shopping_list_items")