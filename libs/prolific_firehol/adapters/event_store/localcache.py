from prolific_firehol.ports import event_store


class LocalCacheStore(event_store.EventStore):
    """
    An implementation of the repository port.
    This adapter saves data by adding it to a list.
    """

    def __init__(self):
        super().__init__()
        self._store = []

    def add(self, item: dict):
        self._store.append(item)
