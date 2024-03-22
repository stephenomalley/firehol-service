import constructs
from aws_cdk import aws_dynamodb
from aws_cdk import aws_lambda
from aws_cdk import aws_lambda_event_sources
from aws_cdk import aws_lambda_python_alpha

from firehol_service import types


class DynamoDBEventStore(constructs.Construct):
    def __init__(
        self,
        scope: constructs.Construct,
        id: str,
        table_details: types.DynamoDBDetails,
        change_stream_lambda_details: types.LambdaDetails,
    ):
        super().__init__(scope, id)
        self.event_store = self.create_build_event_store(scope, table_details)
        self.change_stream_handler = self.create_change_stream_handler(
            scope, change_stream_lambda_details
        )
        self.set_change_steam_handler_event_source(
            self.change_stream_handler, self.event_store
        )

    @staticmethod
    def create_build_event_store(
        scope: constructs.Construct, table_details: types.DynamoDBDetails
    ) -> aws_dynamodb.Table:
        return aws_dynamodb.Table(
            scope,
            partition_key=aws_dynamodb.Attribute(
                name="_PK", type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name="_SK", type=aws_dynamodb.AttributeType.STRING
            ),
            **table_details,
        )

    @staticmethod
    def create_change_stream_handler(
        scope, lambda_details: types.LambdaDetails
    ) -> aws_lambda.Function:
        return aws_lambda_python_alpha.PythonFunction(
            scope,
            **lambda_details,
        )

    @staticmethod
    def grant_write_access(
        event_store: aws_dynamodb.Table, lambda_handler: aws_lambda.IFunction
    ):
        event_store.grant_write_data(lambda_handler)

    @staticmethod
    def set_change_steam_handler_event_source(
        handler: aws_lambda.Function, table: aws_dynamodb.ITable
    ):
        handler.add_event_source(
            aws_lambda_event_sources.DynamoEventSource(
                table=table,
                starting_position=aws_lambda.StartingPosition.LATEST,
                filters=[
                    aws_lambda.FilterCriteria.filter(
                        {"eventName": aws_lambda.FilterRule.is_equal("INSERT")}
                    )
                ],
                batch_size=10,  # Max nb. of events that can be put on the bus at once
            )
        )
