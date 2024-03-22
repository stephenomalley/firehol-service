from typing import TYPE_CHECKING

from prolific_firehol import boto3_session
from prolific_firehol.ports import event_bus

if TYPE_CHECKING:
    from mypy_boto3_events import EventBridgeClient


class EventBridge(event_bus.EventBus):
    def __init__(self):
        self._store: "EventBridgeClient" = self._get_eventbridge_client()

    def add(self, entries: list[dict]):
        self._store.put_events(Entries=entries)

    @staticmethod
    def _get_eventbridge_client() -> "EventBridgeClient":
        return boto3_session.SESSION.client(
            "events", config=boto3_session.SESSION_CONFIG
        )
