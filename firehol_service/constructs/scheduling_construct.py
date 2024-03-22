import constructs
from aws_cdk import aws_events
from aws_cdk import aws_events_targets
from aws_cdk import aws_lambda
from aws_cdk import aws_lambda_python_alpha

from firehol_service import types


class SchedulingConstruct(constructs.Construct):
    """
    A stack for the cron jobs that need to be run for the Firehol service.

    Args:
        scope: The scope of the construct
        id: The id of the construct

    Attributes:
        scheduler_lambda: The lambda function that will be scheduled to run
        cron_schedule: The schedule for the lambda function
        cron_job: The cron job that will be scheduled to run the lambda function

    """

    def __init__(
        self, scope: constructs.Construct, id: str, lambda_details: types.LambdaDetails
    ) -> None:
        super().__init__(scope, id)
        lambda_details.get("layers", []).append(self.git_lambda_layer(scope))
        print(lambda_details)
        self.scheduler_lambda = self.create_cron_schedule_handler(scope, lambda_details)
        self.cron_schedule = self.create_cron_schedule()
        self.cron_job = self.create_cron_schedule_rule(
            scope, self.cron_schedule, self.scheduler_lambda
        )

    @staticmethod
    def create_cron_schedule_handler(
        scope: constructs.Construct, lambda_details: types.LambdaDetails
    ) -> aws_lambda.IFunction:
        """
        Creates a lambda function that will be responsible for accessing github and updating the firehol blocklist.

        Args:
            scope:The stack which the lambda function belongs to.

        Returns:
            a lambda function

        """
        return aws_lambda_python_alpha.PythonFunction(scope, **lambda_details)

    @staticmethod
    def create_cron_schedule() -> aws_events.Schedule:
        """
        A cron schedule that is set to activate once a day

        Returns:
            an aws event schedule.

        """
        return aws_events.Schedule.cron(
            minute="0", hour="4", month="*", week_day="*", year="*"
        )

    @staticmethod
    def create_cron_schedule_rule(
        scope: constructs.Construct,
        cron_schedule: aws_events.Schedule,
        cron_schedule_target: aws_lambda.IFunction,
    ) -> aws_events.IRule:
        """
        Creates a rule which triggers a lambda function on a cron schedule.

        Args:
            scope: The stack which the rule belongs to.
            cron_schedule: The cron schedule for when the rule will trigger.
            cron_schedule_target: The target for the rule.

        Returns:
            A rule which will trigger a lambda when the cron schedule is met.

        """
        return aws_events.Rule(
            scope,
            "FireholBlocklistUpdate",
            schedule=cron_schedule,
            targets=[aws_events_targets.LambdaFunction(cron_schedule_target)],
        )

    @staticmethod
    def git_lambda_layer(scope: constructs.Construct) -> aws_lambda.ILayerVersion:
        return aws_lambda.LayerVersion.from_layer_version_arn(
            scope,
            "git-for-lambdas",
            layer_version_arn="arn:aws:lambda:us-east-1:553035198032:layer:git-lambda2:8",
        )
