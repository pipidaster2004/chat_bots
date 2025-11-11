from bot.handlers.database_logger import DatabaseLogger
from bot.handlers.ensure_user_exists import EnsureUserExists
from bot.handlers.message_start import MessageStart
from bot.handlers.api_sycle import ApiRequest
from bot.handlers.request import AIRequestHandler
from bot.handlers.history import HistoryHandler
from bot.domain.ai_client import AIClient
from bot.handlers.select_model import SelectModel


def get_handlers(ai_client: AIClient):
    return [
        EnsureUserExists(),
        DatabaseLogger(),
        SelectModel(),
        MessageStart(),
        ApiRequest(),
        AIRequestHandler(ai_client),
        HistoryHandler(),
    ]
