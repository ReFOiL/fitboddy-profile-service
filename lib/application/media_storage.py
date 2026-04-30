from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

import anyio
from minio import Minio
from minio.error import S3Error

from application.errors import IntegrationError  # type: ignore[import-not-found]


class MediaValidationError(ValueError):
    pass


@dataclass(slots=True)
class S3MediaStorage:
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    secure: bool
    avatars_prefix: str = "avatars/"
    max_avatar_size_bytes: int = 5 * 1024 * 1024
    _client: Minio = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

    async def upload_avatar(self, *, user_id: str, filename: str, data: bytes) -> str:
        ext, content_type = self._validate_avatar(filename=filename, data=data)
        object_name = await anyio.to_thread.run_sync(self._generate_unique_avatar_object_name, user_id, ext)
        await anyio.to_thread.run_sync(self._put_object_sync, object_name, data, content_type)
        return object_name

    async def download_media(self, object_name: str) -> tuple[bytes, str]:
        return await anyio.to_thread.run_sync(self._download_media_sync, object_name)

    def _put_object_sync(self, object_name: str, data: bytes, content_type: str) -> None:
        try:
            if not self._client.bucket_exists(self.bucket):
                self._client.make_bucket(self.bucket)
            self._client.put_object(
                self.bucket,
                object_name,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
        except Exception as exc:  # pragma: no cover
            raise IntegrationError("failed to upload media to s3") from exc

    def _download_media_sync(self, object_name: str) -> tuple[bytes, str]:
        try:
            response = self._client.get_object(self.bucket, object_name)
            try:
                data = response.read()
                content_type = response.headers.get("Content-Type", "application/octet-stream")
                return data, content_type
            finally:
                response.close()
                response.release_conn()
        except Exception as exc:  # pragma: no cover
            raise IntegrationError("failed to download media from s3") from exc

    def _generate_unique_avatar_object_name(self, user_id: str, ext: str) -> str:
        for _ in range(5):
            candidate = f"{self.avatars_prefix}{user_id}/{uuid4().hex}{ext}"
            if not self._object_exists(candidate):
                return candidate
        raise IntegrationError("failed to generate unique media key")

    def _object_exists(self, object_name: str) -> bool:
        try:
            self._client.stat_object(self.bucket, object_name)
            return True
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
                return False
            raise IntegrationError("failed to check media key collision") from exc

    def _validate_avatar(self, *, filename: str, data: bytes) -> tuple[str, str]:
        if len(data) > self.max_avatar_size_bytes:
            raise MediaValidationError("avatar is too large (max 5MB)")
        ext = Path(filename).suffix.lower()
        allowed: dict[str, str] = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }
        content_type = allowed.get(ext)
        if content_type is None:
            raise MediaValidationError("invalid avatar format (allowed: .jpg, .jpeg, .png, .webp)")
        return ext, content_type
