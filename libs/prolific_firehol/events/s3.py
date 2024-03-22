from prolific_firehol.events import base
from pydantic import computed_field


class S3UploadedEvent(base.Event):
    @computed_field  # type: ignore[misc]
    @property
    def _PK(self) -> str:
        bucket_name = self.detail.data["bucket"]["name"]
        file_name = self.detail.data["object"]["key"]
        return f"BUCKET#{bucket_name}#FILE#{file_name}"

    @computed_field  # type: ignore[misc]
    @property
    def _SK(self) -> str:
        event_id = self.detail.metadata.event_id
        return f"EVENT#{self.detail_type}#{event_id}"
