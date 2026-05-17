"""S3/MinIO storage abstraction.

Env:
    S3_ENDPOINT=https://s3.amazonaws.com (yoki MinIO)
    S3_ACCESS_KEY=...
    S3_SECRET_KEY=...
    S3_BUCKET=unianalytics-uploads

Konfigurasiya yo'q bo'lsa, local filesystem (uploads/) ishlatadi.
"""
import os
from pathlib import Path

from loguru import logger


class S3Storage:
    def __init__(self):
        self.endpoint = os.environ.get("S3_ENDPOINT")
        self.access_key = os.environ.get("S3_ACCESS_KEY")
        self.secret_key = os.environ.get("S3_SECRET_KEY")
        self.bucket = os.environ.get("S3_BUCKET", "unianalytics")
        self.local_dir = Path("uploads")
        self.local_dir.mkdir(exist_ok=True)

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.access_key and self.secret_key)

    def upload(self, key: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        """Yuklash. URLni qaytaradi."""
        if not self.is_configured():
            # Fallback: local
            path = self.local_dir / key
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            return f"/api/v1/uploads/files/{key}"

        try:
            import boto3
            client = boto3.client(
                "s3",
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content,
                ContentType=content_type,
                ACL="public-read",
            )
            return f"{self.endpoint}/{self.bucket}/{key}"
        except ImportError:
            logger.warning("boto3 o'rnatilmagan — local fallback")
            path = self.local_dir / key
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            return f"/api/v1/uploads/files/{key}"
        except Exception as e:
            logger.error("S3 upload error: {}", e)
            return ""

    def delete(self, key: str) -> bool:
        if not self.is_configured():
            try:
                (self.local_dir / key).unlink(missing_ok=True)
                return True
            except Exception:
                return False
        try:
            import boto3
            client = boto3.client(
                "s3",
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception as e:
            logger.error("S3 delete error: {}", e)
            return False


s3 = S3Storage()
