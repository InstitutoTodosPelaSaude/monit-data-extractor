from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from http import HTTPStatus

from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

