from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def persist_update(self, update: dict) -> None:
        pass

    @abstractmethod
    def ensure_user_exists(self, telegram_id: int) -> None:
        pass

    @abstractmethod
    def get_user(self, telegram_id: int) -> dict | None:
        pass

    @abstractmethod
    def add_message(self, telegram_id: int, message_text: str) -> None:
        pass

    @abstractmethod
    def get_last_messages(self, telegram_id: int, limit: int = 5):
        pass

    @abstractmethod
    def set_user_state(self, telegram_id: int, state: dict) -> None:
        pass

    @abstractmethod
    def get_user_state(self, telegram_id: int) -> dict:
        pass
