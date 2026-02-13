from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.dependencies import get_admin_or_manager_user
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание нового заказа"""
    # Сотрудники не могут создавать заказы
    if current_user.role == UserRole.WORKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Сотрудники не могут создавать заказы"
        )
    
    # Обработка товаров (как старых product_id так и новых items)
    items_to_create = []
    if order_in.items:
        items_to_create = order_in.items
    elif order_in.product_id and order_in.quantity:
        items_to_create = [{"product_id": order_in.product_id, "quantity": order_in.quantity}]
    
    if not items_to_create:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ должен содержать хотя бы один товар"
        )
    
    # Определение статуса заказа
    if current_user.role == UserRole.WHOLESALER:
        initial_status = OrderStatus.PENDING
        wholesaler_id = current_user.id
    else:
        initial_status = OrderStatus.ACCEPTED
        wholesaler_id = order_in.wholesaler_id
    
    # Создание заголовка заказа
    db_order = Order(
        # Сохраняем первый товар в заголовок для совместимости
        product_id=items_to_create[0]["product_id"] if isinstance(items_to_create[0], dict) else items_to_create[0].product_id,
        quantity=items_to_create[0]["quantity"] if isinstance(items_to_create[0], dict) else items_to_create[0].quantity,
        deadline=order_in.deadline,
        status=initial_status,
        created_by=current_user.id,
        wholesaler_id=wholesaler_id,
        customer_name=order_in.customer_name,
        customer_phone=order_in.customer_phone,
        customer_address=order_in.customer_address,
        total_price=order_in.total_price,
        prepayment=order_in.prepayment,
        payment_method=order_in.payment_method
    )
    
    db.add(db_order)
    db.flush() # Получаем ID заказа
    
    # Создание позиций заказа
    from app.models.order import OrderItem
    for item in items_to_create:
        p_id = item["product_id"] if isinstance(item, dict) else item.product_id
        qty = item["quantity"] if isinstance(item, dict) else item.quantity
        
        # Проверка товара
        product = db.query(Product).filter(Product.id == p_id).first()
        if not product:
            continue
            
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=p_id,
            quantity=qty,
            price_at_order=product.price
        )
        db.add(db_item)
        
        # Обновление инвентаря
        if initial_status == OrderStatus.ACCEPTED:
            from app.models.production_inventory import ProductionInventory
            inventory = db.query(ProductionInventory).filter(
                ProductionInventory.product_id == p_id,
                ProductionInventory.stage_id == 0
            ).first()
            
            if inventory:
                inventory.quantity += qty
            else:
                inventory = ProductionInventory(product_id=p_id, stage_id=0, quantity=qty)
                db.add(inventory)

    db.commit()
    db.refresh(db_order)
    
    return db_order


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    status: OrderStatus = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка заказов"""
    query = db.query(Order)
    
    # Фильтрация по роли пользователя
    if current_user.role == UserRole.WORKER:
        # Сотрудники видят только заказы в работе
        query = query.filter(Order.status == OrderStatus.IN_PROGRESS)
    elif current_user.role == UserRole.WHOLESALER:
        # Оптовики видят только свои заказы
        query = query.filter(Order.wholesaler_id == current_user.id)
    
    # Фильтрация по статусу
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение заказа по ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Проверка прав доступа
    if current_user.role == UserRole.WHOLESALER and order.wholesaler_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому заказу"
        )
    
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_or_manager_user)
):
    """Обновление статуса заказа (администратор или менеджер)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    old_status = order.status
    order.status = status_update.status
    
    # Если заказ перешел в статус Принят (из Ожидания), добавляем на временный склад
    if status_update.status == OrderStatus.ACCEPTED and old_status == OrderStatus.PENDING:
        from app.models.production_inventory import ProductionInventory
        inventory = db.query(ProductionInventory).filter(
            ProductionInventory.product_id == order.product_id,
            ProductionInventory.stage_id == 0
        ).first()
        if inventory:
            inventory.quantity += order.quantity
        else:
            inventory = ProductionInventory(product_id=order.product_id, stage_id=0, quantity=order.quantity)
            db.add(inventory)

    # Если заказ сдан - списываем товар со склада
    if status_update.status == OrderStatus.DELIVERED and old_status != OrderStatus.DELIVERED:
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product.stock < order.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недостаточно товара на складе. Доступно: {product.stock}"
            )
        product.stock -= order.quantity
        order.delivered_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_or_manager_user)
):
    """Удаление заказа (администратор или менеджер)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    db.delete(order)
    db.commit()
    return None