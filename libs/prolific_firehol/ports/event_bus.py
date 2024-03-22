import abc


class EventBus(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add(self, entries: list):
        pass
