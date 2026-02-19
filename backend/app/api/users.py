from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user, get_password_hash
from app.core.dependencies import get_admin_user
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, User as UserResponse

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    users = db.query(User).all()
    # Pydantic will handle serialization
    return users

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # Check if user with same email or username already exists
    filters = [User.email == user_in.email]
    if user_in.username:
        filters.append(User.username == user_in.username)
        
    existing_user = db.query(User).filter(or_(*filters)).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        phone=user_in.phone,
        address=user_in.address,
        is_active=user_in.is_active
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_in.dict(exclude_unset=True)
    
    # Check uniqueness if changing email or username
    if "email" in update_data and update_data["email"] != user.email:
        existing = db.query(User).filter(User.email == update_data["email"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
            
    if "username" in update_data and update_data["username"] and update_data["username"] != user.username:
        existing = db.query(User).filter(User.username == update_data["username"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
        
    db.delete(user)
    db.commit()

@router.get("/wholesalers")
async def get_wholesalers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    wholesalers = db.query(User).filter(User.role == UserRole.WHOLESALER).all()
    return [
        {
            "id": w.id,
            "full_name": w.full_name,
            "email": w.email,
            "username": w.username,
            "phone": w.phone,
            "address": w.address
        }
        for w in wholesalers
    ]
