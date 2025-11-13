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
        if not ("message" in update and "text" in update["message"]):
            return False

        user_message = update["message"]["text"]
        valid_choices = ["DeepSeek", "Qwen", "GPT", "Gemma"]
        clean_message = user_message.replace("🟢", "").strip()
        return clean_message in valid_choices

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

        clean_choice = user_choice.replace("🟢", "").strip()

        model_mapping = {
            "DeepSeek": "deepseekDeepSeek-R1:novita",
            "Qwen": "Qwen/Qwen3-8B",
            "GPT": "openai/gpt-oss-20b",
            "Gemma": "google/gemma-3-1b-it",
        }

        selected_model = model_mapping[clean_choice]
        storage.set_user_state(telegram_id, {"selected_model": selected_model})
        storage.add_message(telegram_id, f"Selected model: {user_choice}")

        keyboard = self._create_model_keyboard(clean_choice)

        messenger.sendMessage(
            chat_id=chat_id,
            text=f"Select model: {selected_model}\nPlease enter your request:",
            reply_markup=json.dumps(keyboard),
        )

        return HandlerStatus.STOP

    def _create_model_keyboard(self, selected_model: str) -> dict:
        models = ["DeepSeek", "Qwen", "GPT", "Gemma"]

        keyboard_buttons = []
        row = []
        for i, model in enumerate(models):
            if model == selected_model:
                row.append({"text": f"🟢{model}"})
            else:
                row.append({"text": model})

            if (i + 1) % 2 == 0:
                keyboard_buttons.append(row)
                row = []

        return {
            "keyboard": keyboard_buttons,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "selective": True,
        }
