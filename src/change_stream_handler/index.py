import copy
import os

from aws_lambda_powertools.utilities import data_classes
from prolific_firehol import config
from prolific_firehol import events


@data_classes.event_source(data_class=data_classes.DynamoDBStreamEvent)
def handler(db_insert_event: data_classes.DynamoDBStreamEvent, _):
    """
    Lambda that will be triggered when there is an insertion into the dynamodb
    event source table.

    The lambda sends an event to the llm detection event bus. The type of event sent
    depends on what was inserted into the table.

    Args:
        db_insert_event: The event that triggered the lambda
        _: The context of the lambda

    """
    entries: list[dict] = []
    for record in db_insert_event.records:
        if record.dynamodb and record.dynamodb.new_image:
            dynamodb_item = record.dynamodb.new_image
            entries = handle_s3_upload_events(dynamodb_item, entries)

    if entries:
        event_bus = config.EventBus()
        event_bus.add(entries)


def handle_s3_upload_events(dynamodb_item: dict, entries: list[dict]) -> list[dict]:
    """
    Checks if the change stream event for an insert into the event store is a s3
    upload event. If it is a s3 event, then we update the list of `entries`.

    Note: ```entries``` is copied so the original entries dict will remain
    the same on return of this function.

    Args:
        dynamodb_item: a dictionary containing the data that was inserted into the
            event store.
        entries: a list of all events that should get added to the bus.

    Returns:
        A list of the events that have triggered the lambda.

    """
    entries_ = copy.deepcopy(entries)
    if dynamodb_item["detail_type"] == "IPSetFileUploaded":
        event = copy.deepcopy(dynamodb_item)
        s3_upload_event = events.S3UploadedEvent(**event)
        entries_.append(
            s3_upload_event.to_entry(os.getenv("EVENT_BUS_NAME", "firehol_event_bus"))
        )
    return entries_
