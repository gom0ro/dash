from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.dependencies import get_admin_or_manager_user, get_worker_user
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.production_stage import ProductionStage
from app.models.production_inventory import ProductionInventory
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()

# --- WIP / Production Endpoints (MUST be before /{product_id}) ---

@router.get("/wip/pipeline")
async def get_wip_pipeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns aggregated production pipeline data.
    Shows products and their quantity at each stage.
    """
    # Get all inventory records
    inventory_items = db.query(ProductionInventory).all()
    
    # We need to structure this data: Product -> Stages -> Quantity
    # Let's get all products that have inventory > 0
    product_ids = set([item.product_id for item in inventory_items if item.quantity > 0])
    
    if not product_ids:
        return []

    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    
    result = []
    for product in products:
        # Sort stages by order_num
        stages = sorted(product.stages, key=lambda x: x.order_num)
        
        # Build stage info map
        stage_map = {0: {"stage_name": "Склад заготовок", "quantity": 0, "stage_id": 0}}
        for stage in stages:
            stage_map[stage.id] = {
                "stage_id": stage.id,
                "stage_name": stage.name, # Frontend uses stage_name
                "order_num": stage.order_num,
                "payment": stage.payment,
                "quantity": 0
            }
            
        # Fill quantities
        product_inventory = [i for i in inventory_items if i.product_id == product.id]
        total_wip = 0
        
        for item in product_inventory:
            if item.quantity > 0:
                if item.stage_id == 0:
                    stage_map[0]["quantity"] = item.quantity
                else:
                    # Find matching stage
                    if item.stage_id in stage_map:
                        stage_map[item.stage_id]["quantity"] = item.quantity
                total_wip += item.quantity
        
        # Convert stage_map to list, sorted
        # Initial stage (0) first, then actual stages
        stages_list = [stage_map[0]] + [
            stage_map[s.id] for s in stages
        ]
        
        result.append({
            "id": product.id,
            "name": product.name,
            "stock": product.stock,
            "total_wip": total_wip,
            "pipeline": stages_list
        })
        
    return result

@router.get("/wip/tasks")
async def get_wip_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns available production tasks for workers.
    A task is available if there is inventory at the previous stage (stage-1 or 0).
    """
    # Simply return all inventory > 0 where next stage exists
    # But wait, inventory record shows WHERE items currently ARE.
    # If items are at stage 0 (Warehouse), they are ready for Stage 1.
    # If items are at Stage 1, they are ready for Stage 2 (if Stage 2 exists).
    
    inventory_items = db.query(ProductionInventory).filter(ProductionInventory.quantity > 0).all()
    
    tasks = []
    
    for item in inventory_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
            
        # Get stages sorted
        stages = sorted(product.stages, key=lambda x: x.order_num)
        
        if not stages:
            continue
            
        # Determine NEXT stage
        next_stage = None
        current_stage_name = "Склад заготовок"
        
        if item.stage_id == 0:
            # Current is Warehouse, Next is first stage
            if stages:
                next_stage = stages[0]
        else:
            # Current is some stage. Find it in list and get next.
            try:
                # Find index of current stage
                current_stage_obj = next((s for s in stages if s.id == item.stage_id), None)
                if current_stage_obj:
                    current_stage_name = current_stage_obj.name
                    idx = stages.index(current_stage_obj)
                    if idx + 1 < len(stages):
                        next_stage = stages[idx + 1]
                    else:
                        # No next stage -> Ready for Final Warehouse (Finished Goods)
                        # Usually "Finished" is implicit.
                        pass 
            except ValueError:
                continue
                
        if next_stage:
            tasks.append({
                "product_id": product.id,
                "product_name": product.name,
                "current_stage_id": item.stage_id,
                "current_stage_name": current_stage_name,
                "next_stage_id": next_stage.id,
                "next_stage_name": next_stage.name,
                "payment": next_stage.payment,
                "available_quantity": item.quantity
            })
            
    return tasks

@router.get("/wip/inventory")
async def get_wip_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Simple list of all inventory items > 0
    """
    items = db.query(ProductionInventory).filter(ProductionInventory.quantity > 0).all()
    result = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        stage_name = "Склад заготовок"
        if item.stage_id > 0 and product:
            # Find stage name from product stages
            stage = next((s for s in product.stages if s.id == item.stage_id), None)
            if stage:
                stage_name = stage.name
            else:
                stage_name = f"Stage {item.stage_id}"
        
        result.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else "Unknown",
            "stage_id": item.stage_id,
            "stage_name": stage_name,
            "quantity": item.quantity
        })
    return result

# --- Standard Product Endpoints ---

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    products = db.query(Product).all()
    # Pydantic will handle the serialization including nested stages
    return products

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_or_manager_user)
):
    # Check if product with name already exists
    existing_product = db.query(Product).filter(Product.name == product_in.name).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists"
        )

    product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        cost=product_in.cost
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Create production stages if provided
    if product_in.stages:
        for stage_in in product_in.stages:
            stage = ProductionStage(
                product_id=product.id,
                name=stage_in.name,
                order_num=stage_in.order_num,
                payment=stage_in.payment
            )
            db.add(stage)
        db.commit()
        db.refresh(product)
    
    return product

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_or_manager_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = product_in.dict(exclude_unset=True)
    stages_data = update_data.pop("stages", None)
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    if stages_data is not None:
        # Delete old stages and create new ones
        db.query(ProductionStage).filter(ProductionStage.product_id == product.id).delete()
        for stage_in in stages_data:
            stage = ProductionStage(
                product_id=product.id,
                name=stage_in["name"],
                order_num=stage_in["order_num"],
                payment=stage_in["payment"]
            )
            db.add(stage)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_or_manager_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()

@router.post("/{product_id}/produce")
async def produce_product(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_or_manager_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Add to inventory at stage 0 (or first stage)
    # Assuming stage_id=0 represents "Not Started" / "Raw Materials" or just "In Queue"
    
    inventory = db.query(ProductionInventory).filter(
        ProductionInventory.product_id == product_id,
        ProductionInventory.stage_id == 0
    ).first()
    
    if inventory:
        inventory.quantity += quantity
    else:
        inventory = ProductionInventory(
            product_id=product_id,
            stage_id=0,
            quantity=quantity
        )
        db.add(inventory)
    
    db.commit()
    return {"message": "Production launched", "quantity": quantity}

@router.patch("/{product_id}/stock", response_model=ProductResponse)
async def update_stock(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_or_manager_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.stock = quantity
    db.commit()
    db.refresh(product)
    return product
