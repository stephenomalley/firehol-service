from typing import TypedDict

from aws_cdk import Duration
from aws_cdk import RemovalPolicy
from aws_cdk import aws_dynamodb
from aws_cdk import aws_events
from aws_cdk import aws_lambda
from aws_cdk.aws_lambda import Runtime


class LambdaDetails(TypedDict, total=False):
    entry: str
    handler: str
    id: str
    index: str
    layers: list[aws_lambda.ILayerVersion]
    memory_size: int
    retry_attempts: int
    runtime: Runtime
    timeout: Duration
    environment: dict


class QueueDetails(TypedDict, total=False):
    id: str
    queue_name: str
    visibility_timeout: Duration


class DeadLetterQueueDetails(TypedDict, total=False):
    id: str
    queue_name: str
    removal_policy: RemovalPolicy


class IngestionQueueDetails(TypedDict, total=False):
    dead_letter_queue: DeadLetterQueueDetails
    sqs_queue: QueueDetails
    max_receive_count: int


class EventSubscriptionDetails(TypedDict, total=False):
    description: str
    event_bus: aws_events.IEventBus
    event_pattern: aws_events.EventPattern
    id: str
    subscription: str


class NotificationFilter(TypedDict, total=False):
    prefix: str | None
    suffix: str | None


class DynamoDBDetails(TypedDict, total=True):
    id: str
    read_capacity: int
    removal_policy: RemovalPolicy
    stream: aws_dynamodb.StreamViewType
    table_name: str
    write_capacity: int
