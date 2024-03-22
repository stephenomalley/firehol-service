import abc


class FileStore(metaclass=abc.ABCMeta):
    """ """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    @abc.abstractmethod
    def get_content(self, object_key: str) -> str:
        pass

    @abc.abstractmethod
    def upload(self, file_name, file_key):
        pass
