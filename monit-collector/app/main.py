import logging
import os
from http import HTTPStatus

from fastapi import BackgroundTasks, Body, Depends, FastAPI, Header, HTTPException
from dotenv import load_dotenv

from crud import save_sabin_csv_bytes, send_sabin_files_to_server_api

load_dotenv()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

def verify_sabin_api_key(x_api_key: str = Header(None)):
    expected_key = os.getenv("SABIN_API_KEY")
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid or missing API key.")

@app.post("/data/sabin/")
async def upload_sabin_csv(
    data: bytes = Body(...),
    content_type: str = Header(None, alias="content-type"),
    background_tasks: BackgroundTasks = None,
    _: None = Depends(verify_sabin_api_key)
):
    """Recebe um CSV bruto no body (binary) e salva em disco."""

    allowed_types = {"text/csv", "application/csv", "application/octet-stream"}
    if content_type and content_type.split(";")[0].strip().lower() not in allowed_types:
        raise HTTPException(
            status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid content type. Use text/csv."
        )

    try:
        saved_file = save_sabin_csv_bytes(data)
    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("Error saving Sabin upload.")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if background_tasks:
        background_tasks.add_task(send_sabin_files_to_server_api)

    return {
        "status": "accepted",
        "message": "File received and scheduled for processing.",
        "file": saved_file
    }
