import json
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class SelectModel(Handler):
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
            and update["message"]["text"] == "/select"
        )

    def handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ):
        telegram_id = update["message"]["from"]["id"]
        storage.add_message(telegram_id, message)
        messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="Please choose  model",
            reply_markup=json.dumps(
                {
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
            ),
        )
        return HandlerStatus.STOP
