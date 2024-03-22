#!/usr/bin/env python3
import os

import aws_cdk as cdk

from firehol_service.firehol_service_stack import FireholServiceStack


def setup_app():
    app = cdk.App()
    FireholServiceStack(
        app,
        "FireholServiceStack",
        cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    app.synth()


setup_app()
