from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.salary_payment import PaymentType

class SalaryPaymentBase(BaseModel):
    amount: float
    payment_type: PaymentType
    comment: Optional[str] = None

class SalaryPaymentCreate(SalaryPaymentBase):
    worker_id: int

class SalaryPaymentResponse(SalaryPaymentBase):
    id: int
    worker_id: int
    created_at: datetime

    class Config:
        from_attributes = True
