from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.expense import ExpenseType

class ExpenseBase(BaseModel):
    name: Optional[str] = None
    amount: float
    expense_type: ExpenseType
    description: Optional[str] = None
    product_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    expense_type: Optional[ExpenseType] = None
    description: Optional[str] = None
    product_id: Optional[int] = None

class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime
    product_id: Optional[int] = None

    class Config:
        from_attributes = True

class CashWithdrawalBase(BaseModel):
    amount: float
    purpose: Optional[str] = None

class CashWithdrawalCreate(CashWithdrawalBase):
    pass

class CashWithdrawalResponse(CashWithdrawalBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
