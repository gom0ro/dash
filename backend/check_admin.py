from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password, get_password_hash

def check_admin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin").first()
        if user:
            print(f"User found: {user.email}")
            print(f"Role: {user.role}")
            print(f"Hashed password in DB: {user.hashed_password}")
            
            is_valid = verify_password("admin123", user.hashed_password)
            print(f"Password 'admin123' valid: {is_valid}")
            
            if not is_valid:
                print("Resetting password to 'admin123'...")
                user.hashed_password = get_password_hash("admin123")
                db.commit()
                print("Password reset.")
        else:
            print("User 'admin' NOT found!")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin()
