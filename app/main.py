from fastapi import FastAPI

app = FastAPI(title="Fastapi RESTful API")

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI RESTful API"}
