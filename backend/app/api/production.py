from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.production_inventory import ProductionInventory
from app.models.product import Product

router = APIRouter()

@router.get("/inventory")
async def get_production_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    inventory = db.query(ProductionInventory).all()
    result = []
    
    for item in inventory:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        result.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else "Unknown",
            "stage_id": item.stage_id,
            "quantity": item.quantity
        })
    
    return result
