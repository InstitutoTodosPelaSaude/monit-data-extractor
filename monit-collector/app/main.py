from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from http import HTTPStatus

from schema import SabinDataList
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("data/sabin/")
def post_sabin_data(
    sabin_data: SabinDataList,
):
    return {"message": "Data received"}
