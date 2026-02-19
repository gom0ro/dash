from pydantic import BaseModel
from typing import Optional, List

class ProductionStageBase(BaseModel):
    name: str
    order_num: int
    payment: float

class ProductionStageCreate(ProductionStageBase):
    pass

class ProductionStageResponse(ProductionStageBase):
    id: int

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    cost: float = 0
    stock: int = 0

class ProductCreate(ProductBase):
    stages: Optional[List[ProductionStageCreate]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    stock: Optional[int] = None
    stages: Optional[List[ProductionStageCreate]] = None

class ProductResponse(ProductBase):
    id: int
    stages: List[ProductionStageResponse] = []

    class Config:
        from_attributes = True
