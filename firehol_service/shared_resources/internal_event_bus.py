import constructs
from aws_cdk import aws_events


class FireholEventBus(constructs.Construct):
    def __init__(self, scope: constructs.Construct, id: str):
        super().__init__(scope, id)
        self.event_bus = self.create_event_bus(scope)

    @staticmethod
    def create_event_bus(scope: constructs.Construct) -> aws_events.EventBus:
        """
        Creates an event bus that will be used to trigger prolific_firehol.events when a file is written to the storage bucket.

        Args:
            scope: The stack which the event bus belongs to.

        Returns:
            an event bus construct.

        """
        return aws_events.EventBus(
            scope, "FireholBlocklistEventBus", event_bus_name="firehol_event_bus"
        )
