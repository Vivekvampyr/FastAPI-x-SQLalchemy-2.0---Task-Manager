from fastapi import FastAPI
from .routers import auth
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fastapi RESTful API")
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI RESTful API"}
