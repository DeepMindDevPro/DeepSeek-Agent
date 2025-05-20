# examples/example.py
import os
from dotenv import load_dotenv
from deepseek_agent.model import DeepSeekChatModel
from deepseek_agent.assistant import DeepSeekAssistant
from deepseek_agent.tools.web_search import WebSearch

# 加载.env文件
load_dotenv()

# 初始化DeepSeek模型
api_key = os.getenv('DEEPSEEK_API_KEY')
print(api_key)
model_name = 'deepseek-chat'
llm = DeepSeekChatModel(api_key, model_name)

# 初始化Agent
system_message = "You are a helpful assistant."
bot = DeepSeekAssistant(llm=llm, system_message=system_message)

# 定义用户消息
messages = [{"role": "user", "content": "What is the latest news about AI?"}]

# 运行Agent
for response in bot.run(messages):
    print(response)

# 使用工具
web_search = WebSearch()
search_result = web_search.call({'query': 'Latest AI news'})
print(search_result)