import datetime
import json
import uuid

from prolific_firehol import helpers
from pydantic import AliasChoices
from pydantic import Field
from pydantic import main


def uuid_generator() -> str:
    """
    Generates a UUID4 string.

    Returns:
        A UUID4 string

    """
    return str(uuid.uuid4())


class BaseModel(main.BaseModel):
    model_config = main.ConfigDict(extra="ignore")


class EventDetailMetadata(BaseModel):
    event_id: str = Field(default_factory=uuid_generator)
    correlation_id: str = Field(default_factory=uuid_generator)
    event_created_datetime: str = Field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )
    event_version: str = Field(default_factory=lambda: "0")
    external_event: bool = Field(default_factory=lambda: False)
    tags: dict = Field(default_factory=dict)


class EventDetail(BaseModel):
    metadata: EventDetailMetadata
    data: dict


class Event(BaseModel):
    detail: EventDetail = Field(
        ...,
        serialization_alias="Detail",
    )
    detail_type: str = Field(
        ...,
        validation_alias=AliasChoices("detail-type", "detail_type"),
        serialization_alias="DetailType",
    )
    source: str = Field(
        ...,
        serialization_alias="Source",
    )

    def to_entry(self, event_bus_name: str) -> dict:
        """
        Converts an event to a dictionary which can be used as an entry for an
        event bus. The keys to the event are re-mapped to the keys required for an
        event entry and in the case of `Detail` key, the value is converted to a
        json string.

        The event bus that the event will be sent to is ```event_bus_name```.

        Args:
            event_bus_name: The name of the event bus that the entry is being generated
                for.

        Returns:
            a dictionary representing an event entry.
        """
        entry = self.model_dump(exclude={"_PK", "_SK"}, by_alias=True)
        entry |= {
            "Detail": json.dumps(entry.pop("Detail"), cls=helpers.DecimalEncoder),
            "EventBusName": event_bus_name,
        }
        return entry
