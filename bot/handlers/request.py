from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.domain.ai_client import AIClient
from bot.handlers.handler import Handler, HandlerStatus


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

            messenger.deleteMessage(
                chat_id=update["message"]["chat"]["id"],
                message_id=processing_msg["message_id"],
            )
            messenger.sendMessage(
                chat_id=update["message"]["chat"]["id"],
                text=ai_response,
                parse_mode="Markdown",
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
