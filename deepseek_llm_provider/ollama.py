import json

from deepseek_llm_provider.base_provider import BaseLLMProvider
import requests
from typing import Generator  # 用于定义生成器类型


class OllamaProvider(BaseLLMProvider):
    """Ollama本地LLM实现（补充stream_generate方法）"""

    def _validate_config(self):
        required = ['provider_model', 'provider_server_address']
        for key in required:
            if not self.config.get(key):
                raise ValueError(f"Ollama配置缺失: {key}")

    def generate(self, prompt: str, **kwargs) -> str:
        url = f"http://{self.config['provider_server_address']}/api/generate"
        payload = {
            "model": self.config['provider_model'],
            "prompt": prompt,
            **kwargs
        }
        response = requests.post(url, json=payload).json()
        return response['response']

    def stream_generate(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """流式生成实现（返回生成器，逐块输出内容）"""
        url = f"http://{self.config['provider_server_address']}/api/stream"  # Ollama流式接口
        payload = {
            "model": self.config['provider_model'],
            "prompt": prompt,
            **kwargs
        }
        response = requests.post(url, json=payload, stream=True)  # 启用流式响应

        # 逐行解析流式响应（Ollama返回的是NDJSON格式）
        for line in response.iter_lines():
            if line:
                chunk = line.decode('utf-8')
                try:
                    data = json.loads(chunk)
                    if 'response' in data:
                        yield data['response']  # 逐块返回生成的文本
                    if data.get('done', False):  # 生成结束
                        break
                except json.JSONDecodeError:
                    continue