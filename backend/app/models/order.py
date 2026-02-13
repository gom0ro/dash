from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    DELIVERED = "delivered"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    # product_id и quantity остаются для обратной совместимости, но теперь nullable
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    quantity = Column(Integer, nullable=True)
    deadline = Column(DateTime, nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    wholesaler_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)

    # Customer Details
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    customer_address = Column(String, nullable=True)
    
    # Financial Details
    total_price = Column(Float, nullable=True)
    prepayment = Column(Float, default=0)
    payment_method = Column(String, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="orders")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_orders")
    wholesaler = relationship("User", foreign_keys=[wholesaler_id], back_populates="wholesaler_orders")
    work_logs = relationship("WorkLog", back_populates="order", cascade="all, delete-orphan")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f"<Order(id={self.id}, status='{self.status}')>"

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_order = Column(Float, nullable=True)  # Цена на момент заказа

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    __table_args__ = {'extend_existing': True}
