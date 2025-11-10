import json
import urllib.request
import os
from dotenv import load_dotenv

from bot.domain.messenger import Messenger

load_dotenv()


class MessengerTelegram(Messenger):
    def _get_telegram_base_uri(self) -> str:
        return f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

    def _get_telegram_file_uri(self) -> str:
        return f"https://api.telegram.org/file/bot{os.getenv('TELEGRAM_TOKEN')}"

    def makeRequest(self, metgod: str, **params) -> dict:
        json_data = json.dumps(params).encode("utf-8")
        request = urllib.request.Request(
            method="POST",
            url=f"{os.getenv("TELEGRAM_BASE_URI")}/{metgod}",
            data=json_data,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(request) as responce:
            responce_body = responce.read().decode("utf-8")
            responce_json = json.loads(responce_body)
            assert responce_json["ok"]
            return responce_json["result"]

    def getUpdates(self, **params) -> dict:
        return self.makeRequest("getUpdates", **params)

    def sendMessage(self, chat_id: int, text: str, **params) -> dict:
        return self.makeRequest("sendMessage", chat_id=chat_id, text=text, **params)

    def deleteMessage(self, chat_id: int, message_id: int) -> dict:
        return self.makeRequest("deleteMessage", chat_id=chat_id, message_id=message_id)

    def answerCallbackQuery(self, callback_query_id: str, **kwargs) -> dict:
        return self.makeRequest(
            "answerCallbackQuery", callback_query_id=callback_query_id, **kwargs
        )
