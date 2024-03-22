import os

from aws_lambda_powertools.utilities import data_classes
from prolific_firehol import config
from prolific_firehol import events as firehol_events


@data_classes.event_source(data_class=data_classes.SQSEvent)
def handler(sqs_s3_event: data_classes.SQSEvent, _):
    event_store = config.EventStore(
        os.environ.get("EVENT_STORE_TABLE", "firehol_event_store")
    )
    for sqs_record in sqs_s3_event.records:
        for record in sqs_record.json_body.get("Records", []):
            event = {
                "detail": {"metadata": {}, "data": record.get("s3")},
                "detail-type": "IPSetFileUploaded",
                "source": "firehol",
            }
            s3_upload_event = firehol_events.S3UploadedEvent(**event)  # type: ignore
            event_store.add(s3_upload_event.model_dump())
    return {
        "statusCode": 200,
        "body": "This is responsible for handling prolific_firehol.events when a file is uploaded to s3",
    }
