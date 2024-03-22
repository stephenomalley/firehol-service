from typing import TYPE_CHECKING

from prolific_firehol import boto3_session
from prolific_firehol.ports import file_store

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3ServiceResource


class S3FileStore(file_store.FileStore):
    def __init__(self, bucket_name: str):
        super().__init__(bucket_name)
        self._store: "S3ServiceResource" = self._get_s3_client()

    def get_content(self, object_key: str) -> str:
        s3_object = self._store.Object(self.bucket_name, object_key)
        return s3_object.get()["Body"].read().decode("utf-8")

    def upload(self, file_name, file_key):
        bucket = self._store.Bucket(self.bucket_name)
        bucket.upload_file(file_name, file_key)

    @staticmethod
    def _get_s3_client() -> "S3ServiceResource":
        return boto3_session.SESSION.resource("s3", config=boto3_session.SESSION_CONFIG)
