from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.models.user import User
from app.models.expense import Expense
from app.models.cash_withdrawal import CashWithdrawal
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    CashWithdrawalCreate,
    CashWithdrawalResponse
)

router = APIRouter()

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    expense = Expense(
        name=expense_in.name,
        amount=expense_in.amount,
        expense_type=expense_in.expense_type,
        description=expense_in.description,
        product_id=expense_in.product_id
    )
    
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    return expense

@router.get("/", response_model=list[ExpenseResponse])
async def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    try:
        expenses = db.query(Expense).order_by(Expense.created_at.desc()).all()
        return expenses
    except Exception as e:
        print(f"Error getting expenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense

@router.patch("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    update_data = expense_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)
    
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    print(f"Deleting expense with ID: {expense_id}") # Debug log
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        print(f"Expense {expense_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    db.delete(expense)
    db.commit()
    print(f"Expense {expense_id} deleted")

@router.post("/withdrawals", response_model=CashWithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(
    withdrawal_in: CashWithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    withdrawal = CashWithdrawal(
        amount=withdrawal_in.amount,
        purpose=withdrawal_in.purpose
    )
    
    db.add(withdrawal)
    db.commit()
    db.refresh(withdrawal)
    
    return withdrawal

@router.get("/withdrawals", response_model=list[CashWithdrawalResponse])
async def get_withdrawals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    withdrawals = db.query(CashWithdrawal).order_by(CashWithdrawal.created_at.desc()).all()
    return withdrawals
