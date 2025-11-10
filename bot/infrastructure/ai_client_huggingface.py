import json
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

        payload = {
            "inputs": message,
            "parameters": {"max_new_tokens": 500, "temperature": 0.7},
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                api_url, data=data, headers=headers, method="POST"
            )

            with urllib.request.urlopen(request, timeout=100) as response:
                if response.status == 200:
                    response_data = json.loads(response.read().decode("utf-8"))

                    if isinstance(response_data, list) and len(response_data) > 0:
                        return response_data[0].get("generated_text", "No response")
                    elif "generated_text" in response_data:
                        return response_data["generated_text"]
                    else:
                        return str(response_data)
                else:
                    error_text = response.read().decode("utf-8")
                    return f"API Error {response.status}: {error_text[:500]}"

        except Exception as e:
            return f"Error: {str(e)}"
