from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)

    # Relationships
    stages = relationship("ProductionStage", back_populates="product", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="product")
    inventory = relationship("ProductionInventory", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
