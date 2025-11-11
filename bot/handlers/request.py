from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.domain.ai_client import AIClient
from bot.handlers.handler import Handler, HandlerStatus
import re


class AIRequestHandler(Handler):
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def can_handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ):
        if (
            "message" in update
            and "text" in update["message"]
            and not update["message"]["text"].startswith("/")
        ):

            telegram_id = update["message"]["from"]["id"]
            user_state = storage.get_user_state(telegram_id)
            return user_state and "selected_model" in user_state

        return False

    def handle(
        self,
        update: dict,
        message: str,
        storage: Storage,
        messenger: Messenger,
    ):
        telegram_id = update["message"]["from"]["id"]
        user_message = update["message"]["text"]

        storage.add_message(telegram_id, user_message)
        user_state = storage.get_user_state(telegram_id)
        selected_model = user_state.get("selected_model")

        processing_msg = messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"], text="Processing your request..."
        )

        try:
            ai_response = self.ai_client.make_request(selected_model, user_message)
            print(ai_response)
            messenger.deleteMessage(
                chat_id=update["message"]["chat"]["id"],
                message_id=processing_msg["message_id"],
            )
            clean_response = self.smart_format(ai_response)
            messenger.sendMessage(
                chat_id=update["message"]["chat"]["id"],
                text=clean_response,
            )

        except Exception as e:
            messenger.deleteMessage(
                chat_id=update["message"]["chat"]["id"],
                message_id=processing_msg["message_id"],
            )

            messenger.sendMessage(
                chat_id=update["message"]["chat"]["id"],
                text="Error processing your request. Please try again.",
            )
            print(f"AI request error: {e}")

        return HandlerStatus.STOP

    def smart_format(self, text: str) -> str:
        """
        Продвинутое форматирование математических выражений
        """
        text = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"\1 ÷ \2", text)
        text = re.sub(r"\\sqrt\{([^}]+)\}", r"√(\1)", text)
        text = re.sub(r"\^\{([^}]+)\}", r"^\1", text)
        text = re.sub(r"\_\{([^}]+)\}", r"_\1", text)
        text = text.replace("### ", "")
        text = text.replace("1. ", "1. ")
        text = text.replace("2. ", "2. ")
        text = text.replace("3. ", "3. ")
        latex_replacements = {
            "\\cdot": "×",
            "\\times": "×",
            "\\div": "÷",
            "\\implies": "→",
            "\\Rightarrow": "→",
            "\\Leftrightarrow": "↔",
            "\\pm": "±",
            "\\mp": "∓",
            "\\approx": "≈",
            "\\neq": "≠",
            "\\leq": "≤",
            "\\geq": "≥",
            "\\infty": "∞",
            "\\pi": "π",
            "\\alpha": "α",
            "\\beta": "β",
            "\\gamma": "γ",
            "\\delta": "δ",
            "\\epsilon": "ε",
            "\\theta": "θ",
            "\\lambda": "λ",
            "\\mu": "μ",
            "\\sigma": "σ",
            "\\phi": "φ",
            "\\omega": "ω",
            "\\boxed": "",
        }

        for latex_cmd, replacement in latex_replacements.items():
            text = text.replace(latex_cmd, replacement)
        text = text.replace("{", "").replace("}", "")
        text = re.sub(r"\\\[(.*?)\\\]", r"\1", text, flags=re.DOTALL)
        text = re.sub(r"\\\((.*?)\\\)", r"\1", text)
        text = text.replace("\\", "")
        text = text.replace("**", "")

        return text
