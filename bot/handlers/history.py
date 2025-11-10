from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class HistoryHandler(Handler):
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
            and update["message"]["text"] == "/history"
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
        messages = storage.get_last_messages(telegram_id)

        if not messages:
            history_text = "История сообщений пуста."
        else:
            message_list = []
            for i, msg in enumerate(messages):
                message_text = msg[0] or "No text"
                message_date = msg[1]

                if hasattr(message_date, "strftime"):
                    formatted_date = message_date.strftime("%d-%m-%Y %H:%M")
                else:
                    formatted_date = str(message_date)

                message_list.append(f"{i + 1}. {message_text} ({formatted_date})")

            history_text = "Последние 5 сообщений:\n\n" + "\n".join(message_list)

        messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text=history_text,
        )
        return HandlerStatus.STOP
