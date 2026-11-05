from fastapi import FastAPI, HTTPException

from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    price: float = Field(ge=0)
    stock: int = Field(ge=0)

app =  FastAPI()

inventory = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}

@app.post("/items", status_code=201)
def add_item(item: Item):
    if item.name in inventory:
        raise HTTPException(status_code=409, detail=f"Item '{item.name}' already exists")
    inventory[item.name] = item
    return item


