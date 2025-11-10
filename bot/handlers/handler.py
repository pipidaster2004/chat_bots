from abc import ABC, abstractmethod
from enum import Enum

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage


class HandlerStatus(Enum):
    CONTINUE = 1
    STOP = 2


class Handler(ABC):
    @abstractmethod
    def can_handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        pass

    @abstractmethod
    def handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        """
        return: HandlerStatus.CONTINUE:  signal for dispatcher to continue processing
                HandlerStatus.STOP: signal for dispatcher to stop processing
        """
        pass
