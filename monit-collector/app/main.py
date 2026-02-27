import logging
import os
from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import BackgroundTasks, Body, Depends, FastAPI, Header, HTTPException
from dotenv import load_dotenv
from starlette.concurrency import run_in_threadpool

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
    request_ts = datetime.now(timezone.utc).isoformat()
    logging.info(
        "Sabin request received | ts=%s | endpoint=/data/sabin/ | content_type=%s | payload_bytes=%s",
        request_ts,
        content_type,
        len(data),
    )

    allowed_types = {"text/csv", "application/csv", "application/octet-stream"}
    if content_type and content_type.split(";")[0].strip().lower() not in allowed_types:
        response_ts = datetime.now(timezone.utc).isoformat()
        logging.warning(
            "Sabin response sent | ts=%s | endpoint=/data/sabin/ | status=%s | detail=invalid_content_type",
            response_ts,
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        )
        raise HTTPException(
            status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid content type. Use text/csv."
        )

    try:
        saved_file = await run_in_threadpool(save_sabin_csv_bytes, data)
    except HTTPException:
        raise
    except Exception as exc:
        response_ts = datetime.now(timezone.utc).isoformat()
        logging.exception("Error saving Sabin upload.")
        logging.error(
            "Sabin response sent | ts=%s | endpoint=/data/sabin/ | status=%s | detail=save_error",
            response_ts,
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if background_tasks:
        background_tasks.add_task(send_sabin_files_to_server_api, saved_file)

    response_ts = datetime.now(timezone.utc).isoformat()
    logging.info(
        "Sabin response sent | ts=%s | endpoint=/data/sabin/ | status=%s | file=%s",
        response_ts,
        HTTPStatus.ACCEPTED,
        saved_file,
    )

    return {
        "status": "accepted",
        "message": "File received and scheduled for processing.",
        "file": saved_file
    }
