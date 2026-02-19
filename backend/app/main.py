from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, users, products, orders, production, work_logs, salaries, expenses, reports

app = FastAPI(title="Production Management API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(production.router, prefix="/api/v1/production", tags=["production"])
app.include_router(work_logs.router, prefix="/api/v1/work-logs", tags=["work-logs"])
app.include_router(salaries.router, prefix="/api/v1/salaries", tags=["salaries"])
app.include_router(expenses.router, prefix="/api/v1/expenses", tags=["expenses"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "Production Management API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
