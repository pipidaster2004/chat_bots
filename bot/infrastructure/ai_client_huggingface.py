import html
import json
import re
import urllib.request
import os
from dotenv import load_dotenv

from bot.domain.ai_client import AIClient

load_dotenv()


class AIClientHuggingFace(AIClient):
    def make_request(self, model: str, message: str) -> str:
        headers = {
            "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_TOKEN')}",
            "Content-Type": "application/json",
        }
        api_url = os.getenv("HUGGINGFACE_API_URL")

        model_mapping = {
            "deepseek": "deepseek-ai/DeepSeek-R1",
            "qwen": "Qwen/Qwen2.5-72B-Instruct",
            "gemma": "google/gemma-2-9b-it",
            "gpt": "openai/gpt-4",
        }

        for key, value in model_mapping.items():
            if key in model.lower():
                model = value
        payload = {"messages": [{"role": "user", "content": message}], "model": model}

        try:
            data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                api_url, data=data, headers=headers, method="POST"
            )

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

        except Exception as e:
            return f"Error: {str(e)}"
