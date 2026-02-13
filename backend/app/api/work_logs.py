from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.dependencies import get_admin_user
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.work_log import WorkLog
from app.models.production_stage import ProductionStage
from app.models.order import Order
from app.schemas.work_log import WorkLogCreate, WorkLogResponse, MarkAsPaid

router = APIRouter()


@router.post("/", response_model=WorkLogResponse, status_code=status.HTTP_201_CREATED)
async def create_work_log(
    work_log_in: WorkLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Фиксация выполненной работы с перемещением по стадиям"""
    if current_user.role != UserRole.WORKER:
        raise HTTPException(status_code=403, detail="Только воркеры")
    
    # 1. Проверяем этап
    stage = db.query(ProductionStage).filter(ProductionStage.id == work_log_in.stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Этап не найден")
    
    # 2. Проверяем наличие на предыдущем этапе
    from app.models.production_inventory import ProductionInventory
    prev_stage_id = 0
    if stage.order_num > 1:
        prev_stage = db.query(ProductionStage).filter(
            ProductionStage.product_id == work_log_in.product_id,
            ProductionStage.order_num == stage.order_num - 1
        ).first()
        if prev_stage:
            prev_stage_id = prev_stage.id
    
    inv_prev = db.query(ProductionInventory).filter(
        ProductionInventory.product_id == work_log_in.product_id,
        ProductionInventory.stage_id == prev_stage_id
    ).first()
    
    if not inv_prev or inv_prev.quantity < work_log_in.quantity:
        raise HTTPException(status_code=400, detail=f"Недостаточно заготовок на предыдущем этапе. Доступно: {inv_prev.quantity if inv_prev else 0}")
    
    # 3. Перемещаем
    inv_prev.quantity -= work_log_in.quantity
    
    inv_curr = db.query(ProductionInventory).filter(
        ProductionInventory.product_id == work_log_in.product_id,
        ProductionInventory.stage_id == stage.id
    ).first()
    
    if not inv_curr:
        inv_curr = ProductionInventory(product_id=work_log_in.product_id, stage_id=stage.id, quantity=0)
        db.add(inv_curr)
    
    inv_curr.quantity += work_log_in.quantity
    
    # 4. Если это ПОСЛЕДНИЙ этап - зачисляем на основной склад
    from app.models.product import Product
    all_stages = db.query(ProductionStage).filter(ProductionStage.product_id == work_log_in.product_id).all()
    max_order_num = max(s.order_num for s in all_stages)
    
    if stage.order_num == max_order_num:
        product = db.query(Product).filter(Product.id == work_log_in.product_id).first()
        product.stock += work_log_in.quantity
        # После последнего этапа убираем из WIP
        inv_curr.quantity -= work_log_in.quantity
        
    # 5. Создаем лог
    db_work_log = WorkLog(
        product_id=work_log_in.product_id,
        order_id=work_log_in.order_id,
        worker_id=current_user.id,
        stage_id=work_log_in.stage_id,
        quantity=work_log_in.quantity,
        payment=stage.payment * work_log_in.quantity,
        completed_at=datetime.utcnow()
    )
    
    
    db.add(db_work_log)
    
    # 6. Автоматическое обновление статуса заказа
    if work_log_in.order_id and stage.order_num == max_order_num:
        # Если завершили последний этап, проверяем готовность заказа
        order = db.query(Order).filter(Order.id == work_log_in.order_id).first()
        if order:
            # Проверяем, вся ли продукция заказа прошла все этапы
            total_completed = db.query(WorkLog).filter(
                WorkLog.order_id == order.id,
                WorkLog.stage_id == stage.id
            ).count()
            
            # Проверяем количество выполненных работ на последнем этапе
            completed_qty = sum([
                log.quantity for log in db.query(WorkLog).filter(
                    WorkLog.order_id == order.id,
                    WorkLog.stage_id == stage.id
                ).all()
            ])
            
            # Если выполнено >= количества заказа, переводим статус в "Готов"
            from app.models.order import OrderStatus
            if completed_qty >= order.quantity and order.status == OrderStatus.IN_PROGRESS:
                order.status = OrderStatus.DONE
                print(f"✅ Заказ #{order.id} автоматически переведен в статус DONE (готов к выдаче)")
    
    db.commit()
    db.refresh(db_work_log)
    return db_work_log


@router.get("/", response_model=List[WorkLogResponse])
async def get_work_logs(
    worker_id: int = None,
    is_paid: bool = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка записей о работе"""
    query = db.query(WorkLog)
    
    # Сотрудники видят только свои записи
    if current_user.role == UserRole.WORKER:
        query = query.filter(WorkLog.worker_id == current_user.id)
    elif worker_id:
        query = query.filter(WorkLog.worker_id == worker_id)
    
    if is_paid is not None:
        query = query.filter(WorkLog.is_paid == is_paid)
    
    if start_date:
        query = query.filter(WorkLog.completed_at >= start_date)
    if end_date:
        query = query.filter(WorkLog.completed_at <= end_date)
    
    work_logs = query.offset(skip).limit(limit).all()
    return work_logs


@router.get("/my-salary")
async def get_my_salary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение информации о зарплате текущего пользователя"""
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только для сотрудников"
        )
    
    # Все начисления за всё время
    all_logs = db.query(WorkLog).filter(WorkLog.worker_id == current_user.id).all()
    total_earned = sum(log.payment for log in all_logs)
    
    # Все выплаты за всё время
    from app.models.salary_payment import SalaryPayment, PaymentType
    payments = db.query(SalaryPayment).filter(SalaryPayment.worker_id == current_user.id).all()
    
    total_paid_manual = sum(p.amount for p in payments if p.payment_type == PaymentType.SALARY)
    total_advances = sum(p.amount for p in payments if p.payment_type == PaymentType.ADVANCE)
    total_all_money = sum(p.amount for p in payments)
    
    # Баланс = Заработано - Выплачено
    current_balance = total_earned - total_all_money
    
    return {
        "total_earned": total_earned,
        "total_paid": total_paid_manual, 
        "total_unpaid": sum(log.payment for log in all_logs if not log.is_paid),
        "total_advances": total_advances,
        "current_balance": current_balance,
        "unpaid_count": len([l for l in all_logs if not l.is_paid])
    }


@router.post("/mark-paid", status_code=status.HTTP_200_OK)
async def mark_as_paid(
    data: MarkAsPaid,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Отметить записи о работе как выплаченные (только администратор)"""
    work_logs = db.query(WorkLog).filter(WorkLog.id.in_(data.work_log_ids)).all()
    
    if len(work_logs) != len(data.work_log_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Некоторые записи не найдены"
        )
    
    # Группируем логи по сотрудникам
    from collections import defaultdict
    worker_log_totals = defaultdict(float)
    for work_log in work_logs:
        if not work_log.is_paid:
            work_log.is_paid = True
            work_log.paid_at = datetime.utcnow()
            worker_log_totals[work_log.worker_id] += work_log.payment
    
    # Создаем записи о выплатах с учетом авансов
    from app.models.salary_payment import SalaryPayment, PaymentType
    for worker_id, logs_amount in worker_log_totals.items():
        # Считаем текущий баланс ДО этой выплаты
        # Баланс = Заработано_всего - Выплачено_всего
        all_earned = sum(l.payment for l in db.query(WorkLog).filter(WorkLog.worker_id == worker_id).all())
        all_paid = sum(p.amount for p in db.query(SalaryPayment).filter(SalaryPayment.worker_id == worker_id).all())
        
        # До выплаты этих логов (которые уже помечены paid), заработано было столько же.
        # Но баланс показывает сколько мы ДОЛЖНЫ.
        # Если баланс 80к, а логи на 100к, значит 20к уже было выдано авансом.
        current_balance = all_earned - all_paid
        
        # Мы выплачиваем только то, что реально должны (не более суммы логов и не меньше 0)
        actual_payout = max(0, min(logs_amount, current_balance))
        
        if actual_payout > 0:
            db_payment = SalaryPayment(
                worker_id=worker_id,
                amount=actual_payout,
                payment_type=PaymentType.SALARY,
                comment=f"Выплата за {len(work_logs)} этапов (с учетом авансов)"
            )
            db.add(db_payment)
    
    db.commit()
    return {"message": "Успешно обновлено"}
