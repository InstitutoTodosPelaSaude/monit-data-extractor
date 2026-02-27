import csv
import logging
import os
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Iterable

from log import ManagerInterface

SABIN_DIR = os.getenv("SABIN_DATA_DIR", "/data/sabin")
SABIN_PENDING_FILES = os.path.join(SABIN_DIR, "pending_files.txt")
REQUIRED_COLUMNS = [
    "OS",
    "CodigoPosto",
    "Estado",
    "Municipio",
    "DataAtendimento",
    "DataNascimento",
    "Sexo",
    "Descricao",
    "Parametro",
    "Resultado",
    "DataAssinatura",
]
BOOT_WALL_UTC = datetime.now(timezone.utc)
BOOT_MONOTONIC_NS = time.monotonic_ns()
PENDING_FILES_LOCK = threading.Lock()
UPLOAD_DISPATCH_LOCK = threading.Lock()


def ensure_sabin_dir() -> None:
    os.makedirs(SABIN_DIR, exist_ok=True)


def runtime_utc_now() -> datetime:
    """Return UTC wall-clock time derived from process boot wall time and monotonic elapsed time."""
    elapsed_ns = time.monotonic_ns() - BOOT_MONOTONIC_NS
    return BOOT_WALL_UTC + timedelta(microseconds=elapsed_ns // 1_000)


def save_sabin_csv_bytes(data: bytes) -> str:
    """
    Persist raw CSV bytes to disk.

    Returns:
        str: Saved filename.
    """

    ensure_sabin_dir()
    now = runtime_utc_now()
    random_code = f"{secrets.randbelow(10**10):010d}"
    filename = (
        f"sabin_{now.strftime('%Y-%m-%d_%H-%M-%S')}_{int(now.microsecond / 1000):03d}_{random_code}.csv"
    )
    file_path = os.path.join(SABIN_DIR, filename)

    with open(file_path, "wb") as dest:
        dest.write(data)

    try:
        validate_csv_header_plain(file_path)
    except Exception:
        os.remove(file_path)
        raise

    return filename


def validate_csv_header_plain(file_path: str) -> None:
    """
    Validate that the CSV (plain) contains the required columns.
    Only reads the header to avoid loading the whole file.
    """
    with open(file_path, "r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")


def get_manager_interface():
    """
    Retrieve the ManagerInterface instance.
    This function is a placeholder for the actual implementation.
    """

    api_endpoint = os.getenv("MANAGER_ENDPOINT")
    app_name = 'collector'

    if not api_endpoint:
        raise ValueError("MANAGER_ENDPOINT is not set in the environment variables.")
    
    return ManagerInterface(app_name, api_endpoint)

def _dedupe_preserve_order(filenames: Iterable[str]) -> list[str]:
    seen = set()
    normalized = []
    for filename in filenames:
        if not filename or filename in seen:
            continue
        seen.add(filename)
        normalized.append(filename)
    return normalized


def _read_pending_files_unlocked() -> list[str]:
    if not os.path.exists(SABIN_PENDING_FILES):
        return []

    with open(SABIN_PENDING_FILES, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def _write_pending_files_unlocked(pending_files: Iterable[str]) -> None:
    normalized = _dedupe_preserve_order(pending_files)
    if not normalized:
        if os.path.exists(SABIN_PENDING_FILES):
            os.remove(SABIN_PENDING_FILES)
        return

    with open(SABIN_PENDING_FILES, "w", encoding="utf-8") as file:
        for filename in normalized:
            file.write(f"{filename}\n")


def list_pending_files() -> list[str]:
    ensure_sabin_dir()
    with PENDING_FILES_LOCK:
        return _read_pending_files_unlocked()


def persist_pending_files(pending_files: Iterable[str]) -> None:
    ensure_sabin_dir()
    with PENDING_FILES_LOCK:
        _write_pending_files_unlocked(pending_files)


def enqueue_pending_file(filename: str) -> None:
    if not filename:
        return

    ensure_sabin_dir()
    with PENDING_FILES_LOCK:
        pending = _read_pending_files_unlocked()
        _write_pending_files_unlocked([filename, *pending])


def remove_pending_file(filename: str) -> None:
    if not filename:
        return

    ensure_sabin_dir()
    with PENDING_FILES_LOCK:
        pending = _read_pending_files_unlocked()
        _write_pending_files_unlocked([item for item in pending if item != filename])


def send_sabin_files_to_server_api(latest_filename: str) -> None:
    """
    Send the latest Sabin file and any pending files to the server API.
    """
    enqueue_pending_file(latest_filename)

    if not UPLOAD_DISPATCH_LOCK.acquire(blocking=False):
        return

    try:
        try:
            manager_interface = get_manager_interface()
        except Exception:
            logging.exception("Unable to create ManagerInterface.")
            return

        logger = manager_interface.logger
        if not manager_interface.session_id:
            logger.error("No session_id available; postponing Sabin uploads.")
            return

        attempted = set()
        while True:
            pending_now = list_pending_files()
            upload_queue = [name for name in pending_now if name not in attempted]
            if not upload_queue:
                break

            for filename in upload_queue:
                attempted.add(filename)
                if not filename.startswith("sabin_") or not filename.endswith(".csv"):
                    logger.warning(f"Skipping invalid Sabin filename: {filename}")
                    remove_pending_file(filename)
                    continue

                file_path = os.path.join(SABIN_DIR, filename)
                if not os.path.isfile(file_path):
                    logger.warning(f"Skipping missing Sabin file: {file_path}")
                    remove_pending_file(filename)
                    continue

                logger.info(f"Sending file {filename} to server API...")
                try:
                    with open(file_path, "rb") as file_content:
                        manager_interface.upload_file(
                            organization="sabin",
                            project="arbo",
                            file_content=file_content,
                            file_name=filename,
                            content_type="text/csv",
                        )
                        logger.info(f"File {filename} sent to 'arbo' project.")
                        file_content.seek(0)
                        manager_interface.upload_file(
                            organization="sabin",
                            project="respat",
                            file_content=file_content,
                            file_name=filename,
                            content_type="text/csv",
                        )
                        logger.info(f"File {filename} sent to 'respat' project.")
                except Exception:
                    logger.exception(f"Failed to upload {filename}.")
                    continue

                remove_pending_file(filename)
                logger.info(f"File {filename} uploaded successfully to all projects.")

    finally:
        UPLOAD_DISPATCH_LOCK.release()
