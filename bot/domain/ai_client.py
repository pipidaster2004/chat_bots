from abc import ABC, abstractmethod


class AIClient(ABC):
    @abstractmethod
    def make_request(self, model: str, message: str) -> str: ...
