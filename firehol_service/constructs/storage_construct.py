import constructs
from aws_cdk import Duration
from aws_cdk import RemovalPolicy
from aws_cdk import aws_iam
from aws_cdk import aws_s3
from aws_cdk import aws_s3_notifications
from aws_cdk import aws_sqs

from firehol_service import types


class StorageConstruct(constructs.Construct):
    """
    A construct responsible for grouping together the components required to store firehol ipset files taken from
    the firehol ipset blocklist github repository.

    It is responsible for handling the storage of the ipset files in an S3 bucket and triggering an event when a
    file is written into the bucket.

    """

    def __init__(
        self,
        scope: constructs.Construct,
        id: str,
        queue: aws_sqs.IQueue,
        notification_filter: types.NotificationFilter,
    ) -> None:
        super().__init__(scope, id)
        self.storage_bucket = self.create_storage_bucket(scope)
        self.iam_read_only_policy = self.create_iam_read_only_policy(
            scope, self.storage_bucket
        )
        self.add_event_notification(self.storage_bucket, queue, notification_filter)

    @staticmethod
    def create_storage_bucket(scope: constructs.Construct) -> aws_s3.Bucket:
        """
        Create a s3 bucket that blocks public access and removes files if they are older than 4 hours.

        Args:
            scope: The stack which the s3 bucket belongs to

        Returns:
            a s3 bucket construct that can be used to store firehol ipset files

        """
        return aws_s3.Bucket(
            scope,
            "FireholBlocklistStorageBucket",
            bucket_name="firehol-blocklist-storage-bucket",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            lifecycle_rules=[
                aws_s3.LifecycleRule(
                    enabled=True,
                    expiration=Duration.days(1),
                )
            ],
            removal_policy=RemovalPolicy.DESTROY,
        )

    @staticmethod
    def create_iam_read_only_policy(
        scope: constructs.Construct, storage_bucket: aws_s3.Bucket
    ) -> aws_iam.Policy:
        """
        Creates an IAM policy to allow read object access to a s3 bucket.

        Args:
            scope: The stack which the IAM policy belongs to.
            storage_bucket: The S3 bucket that the policy is going to grant access to.

        Returns:
            An IAM policy which can be used give access to the bucket.

        """
        return aws_iam.Policy(
            scope,
            "FireholBlocklistStorageBucketAccessPolicy",
            statements=[
                aws_iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:ListBucket"],
                    resources=[
                        f"arn:aws:s3:::{storage_bucket.bucket_name}",
                        f"arn:aws:s3:::{storage_bucket.bucket_name}/*",
                    ],
                ),
            ],
        )

    @staticmethod
    def add_event_notification(
        s3_bucket: aws_s3.Bucket,
        upload_queue: aws_sqs.IQueue,
        notification_filter: types.NotificationFilter,
    ):
        s3_bucket.add_event_notification(
            aws_s3.EventType.OBJECT_CREATED_PUT,
            aws_s3_notifications.SqsDestination(upload_queue),
            aws_s3.NotificationKeyFilter(**notification_filter),
        )
