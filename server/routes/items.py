from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# ----------------------
# MODELS
# ----------------------

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    price: float

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float


# ----------------------
# "DATABASE"
# ----------------------

database: List[Item] = [
    Item(id=1, name="Item 1", description="Description for Item 1", price=10.99),
    Item(id=2, name="Item 2", description="Description for Item 2", price=20.50)
]


# ----------------------
# ROUTER
# ----------------------

router = APIRouter(prefix="/items", tags=["items"])


# ----------------------
# HELPER
# ----------------------

def find_item(item_id: int) -> Item | None:
    for item in database:
        if item.id == item_id:
            return item
    return None


# ----------------------
# ENDPOINTS
# ----------------------

# READ all
@router.get("/", response_model=List[Item])
def get_items():
    return database


# READ one
@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# CREATE
@router.post("/", response_model=Item, status_code=201)
def create_item(new_item: ItemCreate):
    new_id = max([item.id for item in database], default=0) + 1

    item = Item(
        id=new_id,
        name=new_item.name,
        description=new_item.description,
        price=new_item.price
    )
    database.append(item)
    return item


# UPDATE
@router.put("/{item_id}", response_model=Item)
def update_item(item_id: int, updated_data: ItemCreate):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.name = updated_data.name
    item.description = updated_data.description
    item.price = updated_data.price
    return item


# DELETE
@router.delete("/{item_id}")
def delete_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    database.remove(item)
    return {"result": "Item deleted"}