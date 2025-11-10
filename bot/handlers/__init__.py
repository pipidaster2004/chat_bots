from bot.handlers.message_start import MessageStart
from bot.handlers.api_sycle import ApiRequest
from bot.handlers.request import AIRequestHandler
from bot.handlers.history import HistoryHandler
from bot.domain.ai_client import AIClient
from bot.handlers.select_model import SelectModel


def get_handlers(ai_client: AIClient):
    return [
        MessageStart(),
        ApiRequest(),
        AIRequestHandler(ai_client),
        HistoryHandler(),
        SelectModel(),
    ]
