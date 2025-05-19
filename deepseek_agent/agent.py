# deepseek_agent/agent.py
from abc import ABC, abstractmethod
from typing import List, Dict, Iterator

class Agent(ABC):
    def __init__(self, function_list=None, llm=None, system_message=None):
        self.llm = llm
        self.function_list = function_list
        self.system_message = system_message

    def run(self, messages: List[Dict], **kwargs) -> Iterator[List[Dict]]:
        if self.system_message:
            messages.insert(0, {"role": "system", "content": self.system_message})
        for rsp in self._run(messages=messages, **kwargs):
            yield rsp

    @abstractmethod
    def _run(self, messages: List[Dict], lang: str = 'en', **kwargs) -> Iterator[List[Dict]]:
        raise NotImplementedError