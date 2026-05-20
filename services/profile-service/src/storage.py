import uuid
import boto3
from src.security.config import settings

s3 = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

BUCKET = settings.S3_BUCKET


async def upload_avatar(file):
    ext = file.filename.split(".")[-1]

    filename = f"avatars/{uuid.uuid4()}.{ext}"

    content = await file.read()

    s3.put_object(
        Bucket=BUCKET,
        Key=filename,
        Body=content,
        ContentType=file.content_type
    )

    return f"http://localhost:9000/{BUCKET}/{filename}"