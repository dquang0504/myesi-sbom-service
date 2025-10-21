import os
import json
import aiofiles
import boto3
from botocore.client import Config
from app.core.config import Settings
import uuid

settings = Settings()


async def upload_sbom_json(project_name: str, sbom_json: dict) -> str:
    """
    Upload SBOM JSON to S3 or local folder, return presigned URL or path.
    """
    file_key = f"sboms/{project_name}_{uuid.uuid4()}.json"
    content = json.dumps(sbom_json, indent=2)

    # Local fallback for development
    if not settings.S3_BUCKET:
        local_path = f"./storage/{file_key}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        async with aiofiles.open(local_path, "w") as f:
            await f.write(content)
        return f"file://{local_path}"

    # Real S3 upload
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT or None,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
    )
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=file_key,
        Body=content,
        ContentType="application/json",
    )

    presigned = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": file_key},
        ExpiresIn=3600,
    )
    return presigned
