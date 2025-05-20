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
model_name = ''
llm = DeepSeekChatModel("deepseek-r1:latest", None, "http://localhost:11434/api/chat", "ollama")

# 初始化Agent
system_message = "你是一个中国经济专家"
bot = DeepSeekAssistant(llm=llm, system_message=system_message)

# 定义用户消息
messages = [{"role": "user", "content": "中国的一线城市有哪些"}]

# 运行Agent
for response in bot.run(messages):
    print(response)

# 使用工具
# web_search = WebSearch()
# search_result = web_search.call({'query': '阿里巴巴十八罗汉是那些人'})
# print(search_result)