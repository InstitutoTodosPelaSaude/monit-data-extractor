from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from http import HTTPStatus

from datetime import datetime
import random

from sqlalchemy.orm import Session

from models import get_db
from models import Log, File as FileDB, Status
from models import LogModel, FileModel, StatusModel, StatusUpdateModel


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/log", status_code=HTTPStatus.CREATED)
async def get_log( app_name:str, db: Session = Depends(get_db) ):

    # Session ID is composed of APP-NAME + REQUEST TIMESTAMP + RANDOM NUMBER
    session_id = f"{app_name}-{datetime.now().strftime('%Y%m%d%H%m%S')}-{random.randint(0, 1000000):07d}"
    new_status = Status(session_id=session_id, app_name=app_name, status="STARTED")
    db.add(new_status)
    db.commit()
    db.refresh(new_status)

    return {"session_id": session_id}


@app.post("/log", response_model=LogModel)
async def post_log(log: LogModel, db: Session = Depends(get_db)):

    existing_status = db.query(Status).filter(Status.session_id == log.session_id).first()
    if not existing_status:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session ID not found.")
    
    if log.type == "CRITICAL":
        existing_status.end    = datetime.now()
        existing_status.status = "FINISHED WITH ERRORS"
        db.commit()
        db.refresh(existing_status)
    
    # Remove 'id' if it is present to avoid errors in the database
    log_data = log.dict(exclude={"id"})
    new_log = Log(**log_data)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


@app.put("/status", response_model=StatusUpdateModel)
async def update_status(status_update: StatusUpdateModel, db: Session = Depends(get_db)):

    existing_status = db.query(Status).filter(Status.session_id == status_update.session_id).first()
    if not existing_status:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session ID not found.")

    # Update Status
    existing_status.status = status_update.status
    if status_update.start:
        existing_status.start = status_update.start
    if status_update.end:
        existing_status.end   = status_update.end

    db.commit()
    db.refresh(existing_status)

    return existing_status


@app.post("/file", response_model=FileModel)
async def upload_file(
    session_id: str,
    organization: str,
    project: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    
    existing_status = db.query(Status).filter(Status.session_id == session_id).first()
    if not existing_status:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session ID not found.")
    
    forbidden_extensions = ['.exe']
    if any( [file.filename.endswith(ext) for ext in forbidden_extensions] ):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Invalid file format for {file.filename}')
    
    new_file = FileDB(
        session_id   = session_id,
        organization = organization,
        project      = project,
        filename     = file.filename,
        upload_ts    = datetime.now()
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return new_file