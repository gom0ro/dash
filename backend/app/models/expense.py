from sqlalchemy import Column, Integer, Float, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum

class ExpenseType(str, enum.Enum):
    COST = "cost"
    OTHER = "other"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    expense_type = Column(SQLEnum(ExpenseType), nullable=False)
    description = Column(String, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product")

    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, type='{self.expense_type}')>"
