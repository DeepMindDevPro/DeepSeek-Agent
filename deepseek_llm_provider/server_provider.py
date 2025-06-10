# llm_providers/server_provider.py
from deepseek_llm_provider.base_provider import BaseLLMProvider


class RemoteServerProvider(BaseLLMProvider):
    """远程服务端LLM实现"""

    def _validate_config(self):
        if not self.config.get('provider_server_address'):
            raise ValueError("远程服务地址缺失")

    def generate(self, prompt: str, **kwargs):
        import requests
        url = f"http://{self.config['provider_server_address']}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.config.get('api_key', '')}"}
        payload = {
            "model": self.config['provider_model'],
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=payload).json()
        return response['choices'][0]['message']['content']