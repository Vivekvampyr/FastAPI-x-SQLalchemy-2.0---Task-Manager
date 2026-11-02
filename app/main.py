from fastapi import FastAPI
from .routers import auth, items, inventory
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
title="Inventory Management Enterprise API",
description="RESTful API featuring FastAPI, SQLAlchemy 2.0, direct bcrypt 4.0.1, and 3-tier RBAC.",
version="1.0.0")

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(inventory.router)

@app.get("/")
def root():
    return {"message": "Welcome to Inventory Management Enterprise API"}
