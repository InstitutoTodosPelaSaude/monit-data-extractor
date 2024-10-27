from fastapi import FastAPI, Depends, HTTPException

from datetime import datetime
import random

from sqlalchemy.orm import Session

from models import get_db
from models import Log, File, Status
from models import LogModel, FileModel, StatusModel


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/log", status_code=201)
async def root( app_name:str, db: Session = Depends(get_db) ):

    session_id = f"{app_name}-{datetime.now().strftime('%Y%m%d%H%m%S')}-{random.randint(0, 1000000):07d}"
    new_status = Status(session_id=session_id, app_name=app_name, status="STARTED")
    db.add(new_status)
    db.commit()
    db.refresh(new_status)

    return {"session_id": session_id}


@app.post("/log", response_model=LogModel)
async def post_log(log: LogModel, db: Session = Depends(get_db)):
    # Verifica se o session_id existe no banco de dados
    existing_status = db.query(Status).filter(Status.session_id == log.session_id).first()
    if not existing_status:
        raise HTTPException(status_code=404, detail="Session ID not found.")

    # Remove 'id' if it is present
    log_data = log.dict(exclude={"id"})
    new_log = Log(**log_data)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log