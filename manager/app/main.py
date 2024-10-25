from fastapi import FastAPI, Depends
from datetime import datetime
import random
from sqlalchemy.orm import Session

from models import get_db, Status

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/log")
async def root( app_name:str, db: Session = Depends(get_db) ):

    session_id = f"{app_name}-{datetime.now().strftime('%Y%m%d%H%m%S')}-{random.randint(0, 1000000):07d}"
    new_status = Status(session_id=session_id, app_name=app_name, status="STARTED")
    db.add(new_status)
    db.commit()
    db.refresh(new_status)

    return session_id