from aws_cdk import Environment
from aws_cdk import aws_lambda
from aws_cdk import aws_lambda_python_alpha
from aws_cdk.aws_lambda import Runtime
from constructs import Construct


class DependencyLayers:
    """ """

    def __init__(self, scope: Construct, env: Environment):
        self.layers = [self.powertools_layer(scope, env), self.local_libs_layer(scope)]

    def powertools_layer(self, scope, env) -> aws_lambda.ILayerVersion:
        """
        Gets a layer containing the powertools library.

        Args:
            scope: The construct that the layer will be linked to.
            env: The environment that the stack is being created in.

        Returns:
            A layer containing the powertools library.

        """

        return aws_lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="lambda-powertools",
            layer_version_arn=(
                "arn:aws:lambda:{region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:67"
            ).format(region=env.region),
        )

    def local_libs_layer(self, scope):
        """
        Gets a layer containing the local libs, which include the domains, prolific_firehol.adapters
        and other libraries to be used by the lambda functions.

        Args:
            scope: The construct that the layer will be linked to.

        Returns:
            a layer containing the local libs.

        """
        return aws_lambda_python_alpha.PythonLayerVersion(
            scope,
            "BusinessLogicLayer",
            entry="libs",
            compatible_runtimes=[Runtime.PYTHON_3_12],
        )
