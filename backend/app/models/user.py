from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, or_
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    WORKER = "worker"
    WHOLESALER = "wholesaler"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True) # Making nullable for backward compatibility if needed, but should be filled
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)

    # Relationships
    created_orders = relationship("Order", foreign_keys="Order.created_by", back_populates="creator")
    wholesaler_orders = relationship("Order", foreign_keys="Order.wholesaler_id", back_populates="wholesaler")
    work_logs = relationship("WorkLog", back_populates="worker")
    salary_payments = relationship("SalaryPayment", back_populates="worker")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}', role='{self.role}')>"
