from fastapi import FastAPI, HTTPException

from pydantic import BaseModel, Field, PositiveInt

from fastapi import Depends
from sqlalchemy.orm import Session

from database import SessionLocal, ItemDB


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SaleRequest(BaseModel):
    items: dict[str, PositiveInt]

class Item(BaseModel):
    name: str
    price: float = Field(ge=0)
    stock: int = Field(ge=0)

class StockUpdate(BaseModel):
    change: int


app =  FastAPI()

inventory = {}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/items", status_code=201)
def add_item(item: Item):
    if item.name in inventory:
        raise HTTPException(status_code=409, detail=f"Item '{item.name}' already exists")
    inventory[item.name] = item
    return item

@app.get('/items/{name}', response_model=Item)
def get_item(name: str):
    if name not in inventory:
        raise HTTPException(status_code= 404, detail=f"Item '{name}' not found")
    return inventory[name]

@app.patch('/items/{name}', response_model=Item)
def update_stock(name: str, stock_update: StockUpdate):

    if name not in inventory:
        raise HTTPException(status_code=404, detail=f"Item '{name}' not found!")

    new_stock = inventory[name].stock + stock_update.change


    if new_stock < 0:
        raise HTTPException(status_code= 409, detail="Stock can not be in negative")


    inventory[name].stock = new_stock
    return inventory[name]


@app.post("/sales")
def record_sales(sale: SaleRequest):

    for name, quantity in sale.items.items():
        if name not in inventory:
            raise HTTPException(status_code=404, detail=f"Item '{name}' not found!")
        if quantity > inventory[name].stock:
            raise HTTPException(status_code=409, detail=f"Not enough stock for item '{name}'")

    total = 0    

    for name, quantity in sale.items.items():
        inventory[name].stock -= quantity
        total += inventory[name].price * quantity

    return {"total_revenue": round(total, 2)}
