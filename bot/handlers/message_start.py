import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class MessageStart(Handler):
    def can_handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ):
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    def handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ):
        telegram_id = update["message"]["from"]["id"]
        chat_id = update["message"]["chat"]["id"]
        storage.add_message(telegram_id, message)

        reply_keyboard = {
            "keyboard": [
                [{"text": "DeepSeek"}, {"text": "Qwen"}],
                [{"text": "GPT"}, {"text": "Gemma"}],
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False,
        }

        messenger.sendMessage(
            chat_id=chat_id,
            text="Welcome to AI bot! Choose your model:",
            reply_markup=json.dumps(reply_keyboard),
        )

        return HandlerStatus.STOP
