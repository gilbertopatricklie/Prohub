from fastapi import FastAPI
from app.routers import products, auth

app = FastAPI()

@app.get("/")
def read_root():
    return {"Message": "Welcome to ProHub"}

@app.get("/health")
def get_health():
    return {"Status": "Healthy"}

app.include_router(products.router)
app.include_router(auth.router)
