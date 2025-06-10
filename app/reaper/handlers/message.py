import abc
import logging


class OSCMessageHandler(abc.ABC):
    """Base class for all handlers."""

    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        self._logger = logger
        self.pattern = None
        self.regex = None

    @abc.abstractmethod
    def matches(self, address: str) -> bool:
        """Check if the handler matches the given address."""
        pass

    @abc.abstractmethod
    def handle(self, reaper, address, *args) -> bool:
        """Handle the request for the given address."""
        pass
