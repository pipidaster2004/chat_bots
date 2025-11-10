from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger


class Dispatcher:
    def __init__(self, storage: Storage, messenger: Messenger) -> None:
        self._handlers: list[Handler] = []
        self._storage: Storage = storage
        self._messenger: Messenger = messenger

    def add_handlers(self, *handlers: Handler) -> None:
        for handler in handlers:
            self._handlers.append(handler)

    def dispatch(self, update: dict) -> None:
        message = (
            update["message"]["text"]
            if "message" in update and "text" in update["message"]
            else None
        )

        for handler in self._handlers:
            if handler.can_handle(
                update,
                message,
                self._storage,
                self._messenger,
            ):
                status = handler.handle(
                    update,
                    message,
                    self._storage,
                    self._messenger,
                )
                if status == HandlerStatus.STOP:
                    break
