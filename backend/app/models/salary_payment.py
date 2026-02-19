from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum

class PaymentType(str, enum.Enum):
    SALARY = "salary"
    ADVANCE = "advance"

class SalaryPayment(Base):
    __tablename__ = "salary_payments"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    worker = relationship("User", back_populates="salary_payments")

    def __repr__(self):
        return f"<SalaryPayment(id={self.id}, worker_id={self.worker_id}, amount={self.amount})>"
