from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProductionInventory(Base):
    __tablename__ = "production_inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    stage_id = Column(Integer, nullable=False)  # 0 = temporary warehouse, 1+ = production stages
    quantity = Column(Integer, nullable=False, default=0)

    # Relationships
    product = relationship("Product", back_populates="inventory")

    def __repr__(self):
        return f"<ProductionInventory(product_id={self.product_id}, stage_id={self.stage_id}, quantity={self.quantity})>"
