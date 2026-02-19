from sqlalchemy import Column, Integer, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class WorkLog(Base):
    __tablename__ = "work_logs"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("production_stages.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    payment = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    worker = relationship("User", back_populates="work_logs")
    order = relationship("Order", back_populates="work_logs")
    stage = relationship("ProductionStage", back_populates="work_logs")

    def __repr__(self):
        return f"<WorkLog(id={self.id}, worker_id={self.worker_id}, payment={self.payment})>"
