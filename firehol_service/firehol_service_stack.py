from aws_cdk import Duration
from aws_cdk import Environment
from aws_cdk import RemovalPolicy
from aws_cdk import Stack
from aws_cdk import aws_dynamodb
from aws_cdk import aws_events
from aws_cdk import aws_lambda
from constructs import Construct

from firehol_service.constructs import acl_construct
from firehol_service.constructs import scheduling_construct
from firehol_service.constructs import storage_construct
from firehol_service.shared_resources import dependency_layers
from firehol_service.shared_resources import dynamo_db_event_store
from firehol_service.shared_resources import internal_event_bus


class FireholServiceStack(Stack):
    """
    A stack for the Firehol service.

    Args:
        scope: The scope of the construct
        construct_id: The id of the construct

    Attributes:
        cron_schedule: The stack for the cron jobs that need to be run for the Firehol service.
            contains the lambda function that will be scheduled to run when the cron job is triggered

    """

    def __init__(
        self, scope: Construct, construct_id: str, env: Environment, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.setup_shared_resources(env)
        self.setup_ipset_cron_to_s3_upload(self.internal_event_bus.event_bus)
        self.setup_ipset_processing(
            self.internal_event_bus.event_bus, self.dependency_layers.layers
        )

    def setup_shared_resources(self, env: Environment):
        self.internal_event_bus = internal_event_bus.FireholEventBus(
            self, "FireholEventBus"
        )
        self.dependency_layers = dependency_layers.DependencyLayers(self, env)

        self.event_store = dynamo_db_event_store.DynamoDBEventStore(
            self,
            "FireholeEventStore",
            {
                "id": "FireholeEventStoreDynamoDBTable",
                "read_capacity": 5,
                "removal_policy": RemovalPolicy.DESTROY,
                "stream": aws_dynamodb.StreamViewType.NEW_IMAGE,
                "table_name": "firehol_event_store",
                "write_capacity": 5,
            },
            {
                "entry": "src/change_stream_handler/",
                "id": "FireholDBStreamHandler",
                "retry_attempts": 0,
                "runtime": aws_lambda.Runtime.PYTHON_3_12,
                "memory_size": 1024,
                "timeout": Duration.minutes(5),
                "layers": self.dependency_layers.layers,
                "environment": {"EVENT_BUS_NAME": "firehol_event_bus"},
            },
        )

    def setup_ipset_cron_to_s3_upload(self, event_bus: aws_events.EventBus):
        self.ipset_storage_acl = acl_construct.ACLConstruct(
            self,
            "FireholIPsetStorageACL",
            {
                "entry": "src/ipset_upload_acl/",
                "id": "FireholBlocklistUploadHandler",
                "runtime": aws_lambda.Runtime.PYTHON_3_12,
                "memory_size": 1024,
                "timeout": Duration.minutes(5),
                "layers": self.dependency_layers.layers,
                "environment": {"EVENT_BUS_NAME": "firehol_event_bus"},
            },
            {
                "dead_letter_queue": {
                    "id": "FireholIPsetStorageACLDeadLetterQueue",
                    "queue_name": "firehol_ipset_storage_acl_dead_letter_queue",
                    "removal_policy": RemovalPolicy.DESTROY,
                },
                "sqs_queue": {
                    "id": "FireholIPsetStorageACLQueue",
                    "queue_name": "firehol_ipset_storage_acl_queue",
                    "visibility_timeout": Duration.minutes(5),
                },
                "max_receive_count": 1,
            },
            self.event_store,
        )

        self.storage = storage_construct.StorageConstruct(
            self,
            "FireholServiceStorageConstruct",
            self.ipset_storage_acl.ingestion_queue,
            {"suffix": ".ipset"},
        )

        self.cron_schedule = scheduling_construct.SchedulingConstruct(
            self,
            "FireholServiceCronConstruct",
            {
                "entry": "src/firehol_scheduler/",
                "id": "FireholBlocklistUpdateScheduler",
                "memory_size": 1024,
                "runtime": aws_lambda.Runtime.PYTHON_3_12,
                "timeout": Duration.minutes(15),
                "environment": {
                    "BUCKET_NAME": self.storage.storage_bucket.bucket_name,
                    "EVENT_BUS_NAME": "firehol_event_bus",
                },
                "layers": self.dependency_layers.layers,
            },
        )

        self.storage.storage_bucket.grant_write(self.cron_schedule.scheduler_lambda)

    def setup_ipset_processing(self, event_bus, layers):
        self.ipset_storage_acl = acl_construct.ACLConstruct(
            self,
            "FireholIpSetProcessorACL",
            {
                "entry": "src/ipset_file_processor/",
                "id": "FireholIPSetProcessorHandler",
                "runtime": aws_lambda.Runtime.PYTHON_3_12,
                "memory_size": 1024,
                "timeout": Duration.minutes(5),
                "layers": layers,
                "environment": {"EVENT_BUS_NAME": "firehol_event_bus"},
            },
            {
                "dead_letter_queue": {
                    "id": "FireholIpSetProcessingACLDeadLetterQueue",
                    "queue_name": "firehol_ipset_processing_acl_dead_letter_queue",
                    "removal_policy": RemovalPolicy.DESTROY,
                },
                "sqs_queue": {
                    "id": "FireholIpSetProcessingACLQueue",
                    "queue_name": "firehol_ipset_processing_acl_queue",
                    "visibility_timeout": Duration.minutes(5),
                },
                "max_receive_count": 1,
            },
            self.event_store,
            event_subscription={
                "description": "Rule to consume IPSetFileUploaded events",
                "event_bus": event_bus,
                "event_pattern": aws_events.EventPattern(
                    source=["firehol"], detail_type=["IPSetFileUploaded"]
                ),
                "id": "FireholIpSetProcessingRule",
            },
        )
