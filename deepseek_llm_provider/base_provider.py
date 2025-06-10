# llm_providers/base_provider.py
from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    """抽象LLM服务接口"""

    def __init__(self, config):
        self.config = config  # 包含model、address等配置
        self._validate_config()

    @abstractmethod
    def _validate_config(self):
        """配置有效性验证"""
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """通用生成接口"""
        pass

    @abstractmethod
    def stream_generate(self, prompt: str, **kwargs) -> str:
        """流式生成接口"""
        pass

