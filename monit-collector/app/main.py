import logging
import os
from http import HTTPStatus

from fastapi import BackgroundTasks, Depends, FastAPI, File, Header, HTTPException, UploadFile
from dotenv import load_dotenv

from crud import save_sabin_gzip_upload, send_sabin_files_to_server_api

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
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    _: None = Depends(verify_sabin_api_key)
):
    """Recebe um CSV compactado (gzip) e salva em disco de forma stream-safe."""

    if file.content_type not in {"application/gzip", "application/x-gzip"}:
        raise HTTPException(
            status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid content type. Use application/gzip."
        )

    try:
        saved_file = save_sabin_gzip_upload(file)
    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("Error saving Sabin upload.")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    else:
        try:
            file.file.close()
        except Exception:
            pass

    if background_tasks:
        background_tasks.add_task(send_sabin_files_to_server_api)

    return {
        "status": "accepted",
        "message": "File received and scheduled for processing.",
        "file": saved_file
    }
