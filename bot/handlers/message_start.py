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

        # Вариант 1: Только reply клавиатура
        reply_keyboard = {
            "keyboard": [
                [{"text": "DeepSeek"}, {"text": "Qwen"}],
                [{"text": "GPT"}, {"text": "Gemma"}],
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False,
        }

        inline_keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "DeepSeek",
                        "callback_data": "deepseekDeepSeek-R1:novita",
                    },
                    {"text": "Qwen", "callback_data": "Qwen/Qwen3-8B"},
                ],
                [
                    {"text": "GPT", "callback_data": "openai/gpt-oss-20b"},
                    {
                        "text": "Google Gemma",
                        "callback_data": "google/gemma-3-1b-it",
                    },
                ],
            ]
        }

        messenger.sendMessage(
            chat_id=chat_id,
            text="Welcome to AI bot! Choose your model:",
            reply_markup=json.dumps(reply_keyboard),
        )

        messenger.sendMessage(
            chat_id=chat_id,
            text="Or select using buttons below:",
            reply_markup=json.dumps(inline_keyboard),
        )

        return HandlerStatus.STOP
