import constructs
from aws_cdk import aws_events
from aws_cdk import aws_events_targets
from aws_cdk import aws_lambda_event_sources
from aws_cdk import aws_lambda_python_alpha
from aws_cdk import aws_sqs

from firehol_service import types
from firehol_service.shared_resources import dynamo_db_event_store


class ACLConstruct(constructs.Construct):
    def __init__(
        self,
        scope: constructs.Construct,
        id: str,
        lambda_details: types.LambdaDetails,
        queue_details: types.IngestionQueueDetails,
        event_store_construct: dynamo_db_event_store.DynamoDBEventStore,
        event_subscription: types.EventSubscriptionDetails | None = None,
    ) -> None:
        super().__init__(scope, id)
        self.ingestion_queue = self.create_acl_ingestion_queue(scope, queue_details)
        self.ingestion_handler = self.create_acl_ingestion_handler(
            scope, lambda_details
        )
        self.add_event_source(self.ingestion_handler, self.ingestion_queue)
        self.subscribe_queue_to_events(scope, self.ingestion_queue, event_subscription)

        event_store_construct.grant_write_access(
            event_store_construct.event_store, self.ingestion_handler
        )

    @staticmethod
    def create_acl_ingestion_queue(
        scope: constructs.Construct, queue_details: types.IngestionQueueDetails
    ) -> aws_sqs.IQueue:
        dead_letter_queue = aws_sqs.Queue(scope, **queue_details["dead_letter_queue"])
        return aws_sqs.Queue(
            scope,
            dead_letter_queue=aws_sqs.DeadLetterQueue(
                queue=dead_letter_queue,
                max_receive_count=queue_details["max_receive_count"],
            ),
            **queue_details["sqs_queue"],
        )

    @staticmethod
    def create_acl_ingestion_handler(
        scope, lambda_details: types.LambdaDetails
    ) -> aws_lambda_python_alpha.PythonFunction:
        return aws_lambda_python_alpha.PythonFunction(scope, **lambda_details)

    @staticmethod
    def add_event_source(
        handler: aws_lambda_python_alpha.PythonFunction, queue: aws_sqs.IQueue
    ):
        handler.add_event_source(
            aws_lambda_event_sources.SqsEventSource(
                queue=queue,
                batch_size=1,
            )
        )

    @staticmethod
    def subscribe_queue_to_events(
        scope,
        queue: aws_sqs.IQueue,
        event_subscription_details: types.EventSubscriptionDetails | None,
    ):
        if event_subscription_details is None:
            return
        ingestion_rule = aws_events.Rule(scope, **event_subscription_details)
        ingestion_rule.add_target(
            aws_events_targets.SqsQueue(
                queue=queue,
            )
        )
