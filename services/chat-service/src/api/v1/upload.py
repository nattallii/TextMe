# src/routers/upload.py

import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from src.services.minio import client

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)

BUCKET_NAME = "chat-files"

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

ALLOWED_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "application/pdf",
    "text/plain",
    "application/zip",
}


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
):
    # validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    # read file bytes
    file_bytes = await file.read()

    # validate size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large",
        )

    # generate unique filename
    object_name = (
        f"{uuid.uuid4()}-{file.filename}"
    )

    # upload to minio
    client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
        data=file.file,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=file.content_type,
    )

    # file url
    url = (
        f"http://localhost:9000/"
        f"{BUCKET_NAME}/"
        f"{object_name}"
    )

    return {
        "url": url,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(file_bytes),
    }