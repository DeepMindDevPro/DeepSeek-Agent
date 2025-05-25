# deepseek_agent/agents.py
from typing import List, Iterator, Dict

from deepseek_agent.agent import Agent

# class DeepSeekAssistant(Agent):
#     def _run(self, messages: List[Dict], lang: str = 'en', **kwargs) -> Iterator[List[Dict]]:
#         response = self.llm.chat(messages)
#         for chunk in response:
#             # 处理响应数据，这里简单假设返回的是一个完整的消息
#             yield [chunk]
#


# deepseek_agent/agents.py
from typing import List, Iterator, Dict

from deepseek_agent.agent import Agent

class DeepSeekAssistant(Agent):
    def __init__(self, function_list=None, llm=None, system_message=None):
        super().__init__(function_list, llm, system_message)
        self.history_messages = []  # 用于存储历史消息

    def _run(self, messages: List[Dict], lang: str = 'en', **kwargs) -> Iterator[List[Dict]]:
        # 合并历史消息和当前消息
        all_messages = self.history_messages + messages
        response = self.llm.chat(all_messages)
        for chunk in response:
            # 处理响应数据，这里简单假设返回的是一个完整的消息
            yield [chunk]

    def run(self, messages: List[Dict], **kwargs) -> Iterator[List[Dict]]:
        if self.system_message:
            messages.insert(0, {"role": "system", "content": self.system_message})
        for rsp in self._run(messages=messages, **kwargs):
            # 将用户消息和模型回复添加到历史消息中
            user_message = [msg for msg in messages if msg["role"] == "user"]
            if user_message:
                self.history_messages.extend(user_message)
            model_reply = [{"role": "assistant", "content": rsp[0]["choices"][0]["message"]["content"]}]
            self.history_messages.extend(model_reply)
            yield rsp