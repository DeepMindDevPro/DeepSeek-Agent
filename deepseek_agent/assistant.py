# deepseek_agent/agents.py
from typing import List, Iterator, Dict

from deepseek_agent.agent import Agent

class DeepSeekAssistant(Agent):
    def _run(self, messages: List[Dict], lang: str = 'en', **kwargs) -> Iterator[List[Dict]]:
        response = self.llm.chat(messages)
        for chunk in response:
            # 处理响应数据，这里简单假设返回的是一个完整的消息
            yield [chunk]