from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Items API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

items: list[dict] = []


class ItemCreate(BaseModel):
    name: str
    description: str = ""


class Item(BaseModel):
    id: int
    name: str
    description: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/items", response_model=list[Item])
def list_items():
    return items


@app.post("/items", response_model=Item, status_code=201)
def create_item(payload: ItemCreate):
    item = {"id": len(items) + 1, "name": payload.name, "description": payload.description}
    items.append(item)
    return item


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")
