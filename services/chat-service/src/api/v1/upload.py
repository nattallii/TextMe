# src/routers/upload.py

import uuid
from io import BytesIO

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from src.services.minio import client

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)

BUCKET_NAME = "chat-files"
MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_TYPES = {
    "image/png", "image/jpeg", "image/webp", "image/gif",
    "application/pdf", "text/plain", "application/zip",
}


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    object_name = f"{uuid.uuid4()}-{file.filename}"

    client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
        data=BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=file.content_type,
    )

    # Return proxy URL instead of direct MinIO URL
    url = f"/upload/files/{object_name}"

    return {
        "url": url,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(file_bytes),
    }
# Change in upload.py:
@router.get("/files/{object_name:path}")
async def get_file(object_name: str):
    try:
        response = client.get_object(BUCKET_NAME, object_name)
        content = response.read()
        content_type = response.headers.get("content-type", "application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    return StreamingResponse(
        BytesIO(content),
        media_type=content_type,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=3600",
        },
    )