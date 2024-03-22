from typing import TYPE_CHECKING

from prolific_firehol import boto3_session
from prolific_firehol.ports import event_store

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBStore(event_store.EventStore):
    """
    An implementation of the repository port.
    This adapter saves data by adding it to a DynamoDB table creating a new item
    in the table
    """

    def __init__(self, table_name: str):
        super().__init__(table_name)
        self._store = self._get_db_client()

    def add(self, item: dict):
        self._store.put_item(Item=item)

    def _get_db_client(self) -> "Table":
        return boto3_session.SESSION.resource(
            "dynamodb", config=boto3_session.SESSION_CONFIG
        ).Table(self.table_name)
