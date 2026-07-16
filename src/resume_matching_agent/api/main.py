from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

MAX_FILE_BYTES = 1 * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt"}

app = FastAPI(title="Resume Matching Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_storage_root() -> Path:
    return Path(os.getenv("RMA_STORAGE_ROOT", "data/storage"))


def _validate_txt_upload(file: UploadFile, payload: bytes) -> str:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    if len(payload) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds 1 MB")

    try:
        return payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded") from exc


def _persist_document(kind: str, original_name: str, content: str) -> dict[str, str]:
    now = datetime.now(timezone.utc)
    item_id = str(uuid4())
    status = "Ready for processing" if kind == "resumes" else "Ready for matching"

    root = get_storage_root() / "intake" / kind
    root.mkdir(parents=True, exist_ok=True)

    txt_path = root / f"{item_id}.txt"
    meta_path = root / f"{item_id}.json"

    txt_path.write_text(content, encoding="utf-8")
    meta = {
        "id": item_id,
        "kind": kind,
        "originalFileName": original_name,
        "status": status,
        "storedAtUtc": now.isoformat(),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/intake/resumes/upload")
async def upload_resume(file: UploadFile = File(...)) -> dict[str, str]:
    payload = await file.read()
    content = _validate_txt_upload(file, payload)
    meta = _persist_document("resumes", file.filename or "unknown.txt", content)
    return {
        "resumeId": meta["id"],
        "status": meta["status"],
        "storedAtUtc": meta["storedAtUtc"],
    }


@app.post("/api/v1/intake/requirements/upload")
async def upload_requirement(file: UploadFile = File(...)) -> dict[str, str]:
    payload = await file.read()
    content = _validate_txt_upload(file, payload)
    meta = _persist_document("requirements", file.filename or "unknown.txt", content)
    return {
        "requirementId": meta["id"],
        "status": meta["status"],
        "storedAtUtc": meta["storedAtUtc"],
    }
