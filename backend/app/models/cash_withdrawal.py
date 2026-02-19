from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.core.database import Base

class CashWithdrawal(Base):
    __tablename__ = "cash_withdrawals"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    purpose = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CashWithdrawal(id={self.id}, amount={self.amount})>"
