from typing import Annotated

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel, Field, PositiveInt, StringConstraints

from fastapi import Depends

from sqlalchemy.orm import Session

from database import SessionLocal, ItemDB


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# An item name is used in URLs like /items/{name}, so it must be non-empty after
# trimming spaces, and must not contain "/" (a name with a slash couldn't be fetched
# or updated, because the slash would split the URL path).
ItemName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100, pattern=r"^[^/]+$"),
]

class SaleRequest(BaseModel):
    items: dict[str, PositiveInt]

class Item(BaseModel):
    name: ItemName
    price: float = Field(ge=0)
    stock: int = Field(ge=0)

class StockUpdate(BaseModel):
    change: int


app =  FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/items", status_code=201)
def add_item(item: Item, db: Session = Depends(get_db)):
    existing = db.get(ItemDB, item.name)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Item '{item.name}' already exists")
    db.add(ItemDB(name=item.name, price=item.price, stock=item.stock))
    db.commit()
    return item

@app.get('/items/{name}', response_model=Item)
def get_item(name: str, db: Session = Depends(get_db),):
    item = db.get(ItemDB, name)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item '{name}' not found!")
    return Item(name=item.name, price=item.price, stock=item.stock)

@app.patch('/items/{name}', response_model=Item)
def update_stock(name: str, stock_update: StockUpdate, db: Session = Depends(get_db)):
    item = db.get(ItemDB, name)
    if item is None:
        raise HTTPException(status_code = 404, detail=f"Item '{name}' not found!")

    new_stock = item.stock + stock_update.change

    if new_stock < 0:
        raise HTTPException(status_code=409, detail=f"Stock cannot be negative")
    item.stock = new_stock
    db.commit()
    return Item(name=item.name, price=item.price, stock=item.stock)


@app.post("/sales")
def record_sales(sale: SaleRequest, db: Session = Depends(get_db)):

    for item_name, quantity in sale.items.items():
        item = db.get(ItemDB, item_name)
        if item is None:
            raise HTTPException(status_code=404, detail=f"Item '{item_name}' not found!")
        if item.stock < quantity:
            raise HTTPException(status_code=409, detail=f"Not enough stock for item '{item_name}'")

    total_price = 0

    for item_name, quantity in sale.items.items():
        item = db.get(ItemDB, item_name)
        item.stock -= quantity
        total_price += item.price * quantity
    db.commit()
    return {"total_revenue": round(total_price, 2)}
