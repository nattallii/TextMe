# src/services/storage.py

import uuid
import boto3

from fastapi import UploadFile

from src.security.config import settings


s3 = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

BUCKET = settings.S3_BUCKET


ALLOWED_FILE_TYPES = {
    # images
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",

    # documents
    "application/pdf",
    "text/plain",

    # archives
    "application/zip",

    # office
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


async def upload_chat_file(
    file: UploadFile,
):
    # validate type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise ValueError(
            "Unsupported file type"
        )

    # read content
    content = await file.read()

    # validate size
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(
            "File too large"
        )

    # get extension
    ext = file.filename.split(".")[-1]

    # generate unique name
    filename = (
        f"chat/"
        f"{uuid.uuid4()}."
        f"{ext}"
    )

    # upload to minio / s3
    s3.put_object(
        Bucket=BUCKET,
        Key=filename,
        Body=content,
        ContentType=file.content_type,
    )

    # public file url
    url = (
        f"{settings.S3_ENDPOINT}/"
        f"{BUCKET}/"
        f"{filename}"
    )

    return {
        "url": url,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }