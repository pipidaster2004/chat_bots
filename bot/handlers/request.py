import json
import urllib.request
import html
import re
import os
from dotenv import load_dotenv

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus

load_dotenv()


class AIRequestHandler(Handler):
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
            ai_response = self._make_ai_request(selected_model, user_message)
            messenger.deleteMessage(
                chat_id=update["message"]["chat"]["id"],
                message_id=processing_msg["message_id"],
            )
            messenger.sendMessage(
                chat_id=update["message"]["chat"]["id"], text=ai_response
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

    def _make_ai_request(self, model: str, message: str) -> str:
        headers = {
            "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_TOKEN')}",
            "Content-Type": "application/json",
        }
        api_url = os.getenv("HUGGINGFACE_API_URL")
        model_mapping = {
            "deepseek": "deepseek-ai/DeepSeek-R1",
            "qwen": "Qwen/Qwen2.5-72B-Instruct",
            "gemma": "google/gemma-2-9b-it",  # Проверьте точное название!
            "gpt": "openai/gpt-4",
        }

        # Находим правильное имя модели
        for key, value in model_mapping.items():
            if key in model.lower():
                model = value
        payload = {"messages": [{"role": "user", "content": message}], "model": model}

        try:
            # Подготавливаем запрос
            data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                api_url, data=data, headers=headers, method="POST"
            )

            # Выполняем запрос с таймаутом
            with urllib.request.urlopen(request, timeout=100) as response:
                if response.status == 200:
                    response_data = json.loads(response.read().decode("utf-8"))

                    if response_data and len(response_data) > 0:
                        raw_text = html.unescape(
                            response_data["choices"][0]["message"]["content"]
                        )
                        ai_response = re.sub(
                            r"<think>.*?</think>", "", raw_text, flags=re.DOTALL
                        )
                        ai_response = re.sub(r"\n\s*\n", "\n\n", ai_response).strip()
                    else:
                        ai_response = str(response_data)

                    return ai_response
                else:
                    error_text = response.read().decode("utf-8")
                    return f"Ошибка API (код {response.status}): {error_text[:500]}"

        except urllib.error.URLError as e:
            if hasattr(e, "reason"):
                error_msg = f"Ошибка соединения: {e.reason}"
            elif hasattr(e, "code"):
                error_msg = f"Ошибка HTTP (код {e.code})"
            else:
                error_msg = f"Ошибка сети: {str(e)}"
            return error_msg

        except TimeoutError:
            return "Превышено время ожидания ответа от модели"

        except Exception as e:
            return f"Неожиданная ошибка: {str(e)}"
