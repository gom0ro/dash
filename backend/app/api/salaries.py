from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.dependencies import get_admin_user
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.salary_payment import SalaryPayment, PaymentType
from app.schemas.salary_payment import SalaryPaymentCreate, SalaryPaymentResponse

router = APIRouter()

@router.post("/", response_model=SalaryPaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_in: SalaryPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Выплата зарплаты или аванса сотруднику (только админ)"""
    db_payment = SalaryPayment(
        worker_id=payment_in.worker_id,
        amount=payment_in.amount,
        payment_type=payment_in.payment_type,
        comment=payment_in.comment
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.get("/my-history", response_model=List[SalaryPaymentResponse])
async def get_my_payment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """История всех выплат ТЕКУЩЕМУ сотруднику"""
    payments = db.query(SalaryPayment).filter(SalaryPayment.worker_id == current_user.id).order_by(SalaryPayment.created_at.desc()).all()
    return payments

@router.get("/history/{worker_id}", response_model=List[SalaryPaymentResponse])
async def get_payment_history(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """История всех выплат сотруднику (только админ)"""
    payments = db.query(SalaryPayment).filter(SalaryPayment.worker_id == worker_id).order_by(SalaryPayment.created_at.desc()).all()
    return payments
