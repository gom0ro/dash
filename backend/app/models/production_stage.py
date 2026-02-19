from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProductionStage(Base):
    __tablename__ = "production_stages"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    order_num = Column(Integer, nullable=False)
    payment = Column(Float, nullable=False, default=0)

    # Relationships
    product = relationship("Product", back_populates="stages")
    work_logs = relationship("WorkLog", back_populates="stage")

    def __repr__(self):
        return f"<ProductionStage(id={self.id}, name='{self.name}', order={self.order_num})>"
