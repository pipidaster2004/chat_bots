from abc import ABC, abstractmethod


class Messenger(ABC):
    @abstractmethod
    def getUpdates(**params) -> dict: ...

    @abstractmethod
    def sendMessage(chat_id: int, text: str, **params) -> dict: ...

    @abstractmethod
    def deleteMessage(chat_id: int, message_id: int) -> dict: ...

    @abstractmethod
    def answerCallbackQuery(callback_query_id: str, **kwargs) -> dict: ...
