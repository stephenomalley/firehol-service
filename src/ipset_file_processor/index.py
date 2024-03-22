from aws_lambda_powertools.utilities import data_classes
from prolific_firehol import config


@data_classes.event_source(data_class=data_classes.SQSEvent)
def handler(sqs_event, __):
    for sqs_record in sqs_event.records:
        detail = sqs_record.json_body.get("detail", {})
        bucket: str = detail.get("bucket", {})["name"]
        key: str = detail.get("object", {})["key"]
        file_store = config.FileStore(bucket)
        file_content = file_store.get_content(key)
        print(file_content)
