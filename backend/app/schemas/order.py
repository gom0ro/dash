from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price_at_order: Optional[float] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    """Базовая схема заказа"""
    product_id: Optional[int] = None # Опционально для совместимости
    quantity: Optional[int] = None # Опционально для совместимости
    deadline: datetime
    wholesaler_id: Optional[int] = None
    
    # New Fields
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    total_price: Optional[float] = None
    prepayment: Optional[float] = 0.0
    payment_method: Optional[str] = None


class OrderCreate(OrderBase):
    """Схема для создания заказа"""
    items: Optional[List[OrderItemCreate]] = []


class OrderStatusUpdate(BaseModel):
    """Схема для обновления статуса заказа"""
    status: OrderStatus


class OrderResponse(OrderBase):
    """Схема ответа заказа"""
    id: int
    status: OrderStatus
    created_by: int
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
