from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.domain.ai_client import AIClient
from bot.dispatcher import Dispatcher
from bot.infrastructure.messenger_telegram import MessengerTelegram
from bot.infrastructure.storage_sqlite import StorageSqlite
from bot.infrastructure.ai_client_huggingface import AIClientHuggingFace
import bot.long_polling


def main() -> None:
    try:
        storage: Storage = StorageSqlite()
        messenger: Messenger = MessengerTelegram()
        ai_client: AIClient = AIClientHuggingFace()

        dispatcher = Dispatcher(storage, messenger)
        from bot.handlers import get_handlers

        handlers = get_handlers(ai_client)
        dispatcher.add_handlers(*handlers)

        bot.long_polling.start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        print("Bye!")


if __name__ == "__main__":
    main()
