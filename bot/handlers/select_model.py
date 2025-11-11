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
        if not ("message" in update and "text" in update["message"]):
            return False

        user_message = update["message"]["text"]
        valid_choices = ["DeepSeek", "Qwen", "GPT", "Gemma"]
        return user_message in valid_choices

    def handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ):
        telegram_id = update["message"]["from"]["id"]
        chat_id = update["message"]["chat"]["id"]
        user_choice = update["message"]["text"]

        model_mapping = {
            "DeepSeek": "deepseekDeepSeek-R1:novita",
            "Qwen": "Qwen/Qwen3-8B",
            "GPT": "openai/gpt-oss-20b",
            "Gemma": "google/gemma-3-1b-it",
        }

        selected_model = model_mapping[user_choice]
        storage.set_user_state(telegram_id, {"selected_model": selected_model})
        storage.add_message(telegram_id, f"Selected model: {user_choice}")

        messenger.sendMessage(
            chat_id=chat_id,
            text=f"Select model using inline buttons: {selected_model}\nPlease enter your request:",
        )

        return HandlerStatus.STOP
