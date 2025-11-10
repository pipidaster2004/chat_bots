from bot.handlers.api_sycle import ApiRequest
from bot.handlers.handler import Handler
from bot.handlers.database_logger import DatabaseLogger
from bot.handlers.ensure_user_exists import EnsureUserExists
from bot.handlers.history import HistoryHandler
from bot.handlers.message_start import MessageStart
from bot.handlers.request import AIRequestHandler
from bot.handlers.select_model import SelectModel


def get_handlers() -> list[Handler]:
    return [
        DatabaseLogger(),
        HistoryHandler(),
        EnsureUserExists(),
        MessageStart(),
        ApiRequest(),
        AIRequestHandler(),
        SelectModel(),
    ]
