from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WorkLogBase(BaseModel):
    order_id: Optional[int] = None
    product_id: int
    stage_id: int
    quantity: int

class WorkLogCreate(WorkLogBase):
    pass

class WorkLogResponse(WorkLogBase):
    id: int
    worker_id: int
    payment: float
    is_paid: bool
    completed_at: datetime
    product_name: Optional[str] = None
    stage_name: Optional[str] = None

    class Config:
        from_attributes = True

class MarkAsPaid(BaseModel):
    work_log_ids: list[int]
