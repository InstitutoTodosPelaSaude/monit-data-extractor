from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Request

from http import HTTPStatus
import os
from dotenv import load_dotenv

from crud import save_sabin_data_flow

from schema import SabinDataList
from datetime import datetime

load_dotenv()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

from fastapi import Header

def verify_sabin_api_key(x_api_key: str = Header(None)):
    expected_key = os.getenv("SABIN_API_KEY")
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid or missing API key.")

@app.post("/data/sabin/")
def post_sabin_data(
    sabin_data: SabinDataList,
    _: None = Depends(verify_sabin_api_key)
):
    """
    Save Sabin data to the database and format it to JSON.

    Args:
        sabin_data (SabinDataList): The data to be saved.
    """
    try:
        save_sabin_data_flow(sabin_data)
        return {
            "status": "success",
            "message": "Data received successfully.",
            "received_count": len(sabin_data.data) if hasattr(sabin_data, 'data') else None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "received_count": 0
        }
