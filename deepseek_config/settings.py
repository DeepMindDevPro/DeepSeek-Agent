# config/settings.py
import configparser

from deepseek_llm_provider.ollama import OllamaProvider
from deepseek_llm_provider.server_provider import RemoteServerProvider

class AppConfig:
    """配置解析器"""

    def __init__(self, config_path="config.ini"):
        self.parser = configparser.ConfigParser()
        self.parser.read(config_path)
        self.main = dict(self.parser['MAIN'])
        self.browser = dict(self.parser['BROWSER'])

    def get_llm_provider(self):
        """根据配置初始化LLM提供器"""
        provider_map = {
            "ollama": OllamaProvider,
            "server": RemoteServerProvider
            # "lm-studio": LMStudioProvider  # 类似实现
        }
        provider_cls = provider_map[self.main['provider_name']]
        return provider_cls(self.main)