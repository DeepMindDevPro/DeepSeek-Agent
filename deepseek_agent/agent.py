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


#定义专用 Agent 类：继承 Agent 基类（agent.py), 为不同任务场景实现专用代理
class CoderAgent(Agent):
    def _run(self, messages: List[Dict], lang: str = 'en', **kwargs) -> Iterator[List[Dict]]:
        # 专注代码生成/调试的逻辑（调用代码相关工具或 LLM 指令微调）
        response = self.llm.chat(messages + [{"role": "system", "content": "你是专业的代码生成助手"}])
        for chunk in response:
            yield [chunk]

# 浏览器助手
class BrowserAgent(Agent):
    def _run(self, messages: List[Dict], lang: str = 'en', **kwargs) -> Iterator[List[Dict]]:
        # 集成浏览器操作工具（如Selenium/Playwright）
        from deepseek_agent.tools.web_search import WebSearch
        browser_tool = WebSearch()
        result = browser_tool.call({"query": messages[-1]["content"]})
        yield [{"role": "assistant", "content": result}]
