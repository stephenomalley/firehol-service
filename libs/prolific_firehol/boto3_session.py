import boto3
from botocore import config


def boto_3_session():
    session = boto3.Session()
    session_config = config.Config(tcp_keepalive=True)
    return session, session_config


SESSION, SESSION_CONFIG = boto_3_session()
