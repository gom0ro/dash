import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole

# For development: remove existing DB to apply schema changes cleanly
if os.path.exists("production_v3.db"):
    try:
        os.remove("production_v3.db")
        print("Old database removed.")
    except PermissionError:
        print("Could not delete production_v3.db, assuming locked. Tables might not update.")

# Create tables with NEW schema
Base.metadata.create_all(bind=engine)
print("Database tables created.")

def create_initial_data(db: Session):
    # Check if admin already exists
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin_user = User(
            email="admin@example.com",
            username="admin",
            full_name="Administrator",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created: admin / admin123")
    else:
        print("Admin user already exists")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_initial_data(db)
    finally:
        db.close()
