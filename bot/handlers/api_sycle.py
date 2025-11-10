
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class ApiRequest(Handler):
    def can_handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ):
        return "callback_query" in update

    def handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ):
        callback_data = update["callback_query"]["data"]
        telegram_id = update["callback_query"]["from"]["id"]
        storage.set_user_state(telegram_id, {"selected_model": callback_data})
        storage.add_message(telegram_id, f"Selected model: {callback_data}")
        messenger.answerCallbackQuery(update["callback_query"]["id"])

        messenger.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        messenger.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text=f"Selected model: {callback_data}\nPlease enter your request:",
        )
        return HandlerStatus.STOP
