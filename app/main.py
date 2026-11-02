from fastapi import FastAPI
from .routers import auth, items, inventory
from .database import Base, engine
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .core.rate_limiter import limiter

Base.metadata.create_all(bind=engine)

app = FastAPI(
title="Inventory Management Enterprise API",
description="RESTful API featuring FastAPI, SQLAlchemy 2.0, direct bcrypt 4.0.1, and 3-tier RBAC.",
version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(inventory.router)

@app.get("/")
def root():
    return {"message": "Welcome to Inventory Management Enterprise API"}
