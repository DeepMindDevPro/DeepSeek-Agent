# deepseek_agent/tools/base.py
from abc import ABC, abstractmethod
from typing import Dict, Union

class BaseTool(ABC):
    def __init__(self, cfg: Dict = None):
        self.cfg = cfg or {}

    @abstractmethod
    def call(self, params: Union[str, dict], **kwargs):
        raise NotImplementedError

    def _verify_json_format_args(self, params):
        if isinstance(params, str):
            import json
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                pass
        return params