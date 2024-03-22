import abc
from typing import TYPE_CHECKING
from typing import Union

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table

Resource = Union[list, "Table"]


class EventStore(metaclass=abc.ABCMeta):
    """
    The interface (port) for an event store
    """

    def __init__(self, table_name: str):
        self._store: Resource
        self.table_name = table_name

    @abc.abstractmethod
    def add(self, item: dict):
        pass
