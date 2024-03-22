import os

from prolific_firehol.adapters import event_bus
from prolific_firehol.adapters import event_store
from prolific_firehol.adapters import file_store

EventStore = {
    "local": event_store.LocalCacheStore,
    "dynamodb": event_store.DynamoDBStore,
}[os.environ.get("EVENT_STORE_ADAPTER", "dynamodb")]

FileStore = {"s3": file_store.S3FileStore}[os.environ.get("FILE_STORE_ADAPTER", "s3")]
EventBus = {"eventbridge": event_bus.EventBridge}[
    os.environ.get("EVENT_BUS_ADAPTER", "eventbridge")
]
