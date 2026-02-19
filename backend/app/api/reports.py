from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.core.dependencies import get_admin_user
from app.core.database import get_db
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.expense import Expense, ExpenseType
from app.models.work_log import WorkLog
from app.models.cash_withdrawal import CashWithdrawal
from app.models.salary_payment import SalaryPayment, PaymentType
from app.schemas.expense import CashWithdrawalCreate, CashWithdrawalResponse

router = APIRouter()


@router.get("/cash")
async def get_cash_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Финансовый отчет по кассе (только администратор)"""
    query_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED)
    query_expenses = db.query(Expense)
    query_work_logs = db.query(WorkLog)
    query_withdrawals = db.query(CashWithdrawal)
    
    # Фильтрация по датам
    if start_date:
        query_orders = query_orders.filter(Order.delivered_at >= start_date)
        query_expenses = query_expenses.filter(Expense.created_at >= start_date)
        query_work_logs = query_work_logs.filter(WorkLog.completed_at >= start_date)
        query_withdrawals = query_withdrawals.filter(CashWithdrawal.withdrawn_at >= start_date)
    
    if end_date:
        query_orders = query_orders.filter(Order.delivered_at <= end_date)
        query_expenses = query_expenses.filter(Expense.created_at <= end_date)
        query_work_logs = query_work_logs.filter(WorkLog.completed_at <= end_date)
        query_withdrawals = query_withdrawals.filter(CashWithdrawal.withdrawn_at <= end_date)
    
    # Получение данных
    delivered_orders = query_orders.all()
    all_expenses = query_expenses.all()
    all_work_logs = query_work_logs.all()
    all_withdrawals = query_withdrawals.all()
    
    # Расчет продаж
    sales = 0
    for order in delivered_orders:
        if order.total_price:
            sales += order.total_price
        else:
            product = db.query(Product).filter(Product.id == order.product_id).first()
            if product:
                sales += order.quantity * product.price
    
    # Расчет себестоимости
    cost_of_goods = 0
    for order in delivered_orders:
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            cost_of_goods += order.quantity * product.cost
    
    # Расчет расходов
    cost_expenses = sum(e.amount for e in all_expenses if e.expense_type == ExpenseType.COST)
    other_expenses = sum(e.amount for e in all_expenses if e.expense_type == ExpenseType.OTHER)
    total_expenses = cost_expenses + other_expenses
    
    # Расчет зарплат (начисления)
    total_salaries = sum(log.payment for log in all_work_logs)
    paid_salaries = sum(log.payment for log in all_work_logs if log.is_paid)
    unpaid_salaries = sum(log.payment for log in all_work_logs if not log.is_paid)

    # Зарплаты и Авансы (Оплаты)
    # Считаем реальный отток денег
    salary_payments_sum = db.query(func.sum(SalaryPayment.amount)).scalar() or 0
    
    # Изъятия
    total_withdrawals = sum(w.amount for w in all_withdrawals)
    
    # Итоговые расчеты
    gross_profit = sales - cost_of_goods - cost_expenses
    net_profit = gross_profit - other_expenses - total_salaries
    # Баланс в кассе: продажи - расходы - реальные выплаты - изъятия
    cash_balance = sales - total_expenses - salary_payments_sum - total_withdrawals
    
    return {
        "sales": sales,
        "cost_of_goods": cost_of_goods,
        "cost_expenses": cost_expenses,
        "other_expenses": other_expenses,
        "total_expenses": total_expenses,
        "total_salaries": total_salaries,
        "paid_salaries": paid_salaries,
        "unpaid_salaries": unpaid_salaries,
        "total_withdrawals": total_withdrawals,
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "cash_balance": cash_balance
    }


@router.post("/cash/withdraw", response_model=CashWithdrawalResponse)
async def withdraw_cash(
    withdrawal_in: CashWithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Изъятие денег из кассы (только администратор)"""
    db_withdrawal = CashWithdrawal(
        amount=withdrawal_in.amount,
        withdrawn_by=current_user.id,
        note=withdrawal_in.note
    )
    
    db.add(db_withdrawal)
    db.commit()
    db.refresh(db_withdrawal)
    
    return db_withdrawal


@router.get("/sales")
async def get_sales_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Отчет по продажам (только администратор)"""
    query = db.query(Order).filter(Order.status == OrderStatus.DELIVERED)
    
    if start_date:
        query = query.filter(Order.delivered_at >= start_date)
    if end_date:
        query = query.filter(Order.delivered_at <= end_date)
    
    orders = query.all()
    
    # Группировка по товарам
    sales_by_product = {}
    total_revenue = 0
    
    for order in orders:
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            revenue = order.total_price if order.total_price else (order.quantity * product.price)
            total_revenue += revenue
            
            if product.id not in sales_by_product:
                sales_by_product[product.id] = {
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity_sold": 0,
                    "revenue": 0
                }
            
            sales_by_product[product.id]["quantity_sold"] += order.quantity
            sales_by_product[product.id]["revenue"] += revenue
    
    return {
        "total_orders": len(orders),
        "total_revenue": total_revenue,
        "sales_by_product": list(sales_by_product.values())
    }


@router.get("/workers")
async def get_workers_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Отчет по эффективности сотрудников (только администратор)"""
    query = db.query(WorkLog)
    
    if start_date:
        query = query.filter(WorkLog.completed_at >= start_date)
    if end_date:
        query = query.filter(WorkLog.completed_at <= end_date)
    
    work_logs = query.all()
    
    # Группировка по сотрудникам
    workers_stats = {}
    
    # 1. Считаем начисления по логам
    for log in work_logs:
        worker = db.query(User).filter(User.id == log.worker_id).first()
        if worker:
            if worker.id not in workers_stats:
                workers_stats[worker.id] = {
                    "worker_id": worker.id,
                    "worker_name": worker.full_name,
                    "worker_phone": worker.phone,
                    "stages_completed": 0,
                    "total_earned": 0,
                    "total_paid": 0,
                    "total_unpaid": 0,
                    "total_advances": 0,
                    "current_balance": 0,
                    "top_product": "—",
                    "avg_daily": 0,
                    "days_active": set(), # Use a set to track unique dates
                    "product_counts": {} # Temporary helper
                }
            
            # Начисления
            stats = workers_stats[log.worker_id]
            stats["stages_completed"] += 1
            stats["total_earned"] += log.payment
            if log.is_paid:
                stats["total_paid"] += log.payment
            else:
                stats["total_unpaid"] += log.payment
            
            # Top product tracking
            # Ensure log.product is loaded or joined
            if log.product_id:
                product = db.query(Product).filter(Product.id == log.product_id).first()
                p_name = product.name if product else "N/A"
            else:
                p_name = "N/A"
            stats["product_counts"][p_name] = stats["product_counts"].get(p_name, 0) + 1
            
            # Keep track of active days
            stats["days_active"].add(log.completed_at.date())

    # 2. Считаем выплаты и финализируем статистику
    for worker_id, stats in workers_stats.items():
        # Source of truth for all money given to worker
        all_payments = db.query(SalaryPayment).filter(SalaryPayment.worker_id == worker_id).all()
        
        total_advances = sum(p.amount for p in all_payments if p.payment_type == PaymentType.ADVANCE)
        total_salary_payouts = sum(p.amount for p in all_payments if p.payment_type == PaymentType.SALARY)
        total_all_money = sum(p.amount for p in all_payments)
        
        stats["total_advances"] = total_advances
        # Real balance = Everything Earned - Everything Paid
        stats["current_balance"] = stats["total_earned"] - total_all_money
        
        # Performance Finalization
        if stats["product_counts"]:
            stats["top_product"] = max(stats["product_counts"], key=stats["product_counts"].get)
        
        days_count = len(stats["days_active"])
        if days_count > 0:
            stats["avg_daily"] = stats["total_earned"] / days_count
        
        # Clean up temporary fields
        del stats["days_active"]
        del stats["product_counts"]

    return {"workers": list(workers_stats.values())}


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Статистика для графиков (за последние 30 дней)"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # 1. Продажи по дням
    daily_sales = []
    curr = start_date
    while curr <= end_date:
        day_start = curr.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = curr.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Сумма выполненных заказов за этот день
        day_orders = db.query(Order).filter(
            Order.status == OrderStatus.DELIVERED,
            Order.delivered_at >= day_start,
            Order.delivered_at <= day_end
        ).all()
        
        sum_day = 0
        for o in day_orders:
            sum_day += o.total_price if o.total_price else (o.quantity * o.product.price)
            
        daily_sales.append({
            "date": curr.strftime("%d.%m"),
            "amount": sum_day
        })
        curr += timedelta(days=1)
        
    # 2. Самые продаваемые товары
    top_products = db.query(
        Product.name,
        func.sum(Order.quantity).label("total_qty")
    ).join(Order).filter(
        Order.status == OrderStatus.DELIVERED
    ).group_by(Product.name).order_by(func.sum(Order.quantity).desc()).limit(5).all()
    
    # 3. Эффективность сотрудников (за последние 30 дней)
    worker_performance = db.query(
        User.full_name,
        func.count(WorkLog.id).label("logs_count")
    ).join(WorkLog).filter(
        WorkLog.completed_at >= start_date
    ).group_by(User.full_name).order_by(func.count(WorkLog.id).desc()).limit(5).all()

    return {
        "daily_sales": daily_sales,
        "top_products": [{"name": p[0], "value": p[1]} for p in top_products],
        "worker_performance": [{"name": w[0], "value": w[1]} for w in worker_performance]
    }