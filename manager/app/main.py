from fastapi import FastAPI
from datetime import datetime
import random


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/log")
async def root( app_name:str ):
    return f"{app_name}-{datetime.now().strftime('%Y%m%d%H%m%S')}-{random.randint(0, 1000000):07d}"