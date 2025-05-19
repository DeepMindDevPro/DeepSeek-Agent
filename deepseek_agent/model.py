# deepseek_agent/model.py
import requests

class DeepSeekChatModel:
    def __init__(self, api_key, model_name, api_url="https://platform.deepseek.com/api/chat"):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = api_url

    def chat(self, messages, functions=None, stream=False, extra_generate_cfg=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model_name,
            "messages": messages
        }
        if functions:
            data["functions"] = functions
        if extra_generate_cfg:
            data.update(extra_generate_cfg)

        response = requests.post(self.api_url, headers=headers, json=data, stream=stream)
        if stream:
            for line in response.iter_lines():
                if line:
                    yield line
        else:
            yield response.json()