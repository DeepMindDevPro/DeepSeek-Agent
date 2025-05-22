import os
from dotenv import load_dotenv
from deepseek_agent.model import DeepSeekChatModel
from deepseek_agent.assistant import DeepSeekAssistant
from deepseek_agent.tools.rag_tool import RAGTool, add_document

# 加载 .env 文件
load_dotenv()

# 初始化 DeepSeek 模型
api_key = os.getenv('DEEPSEEK_API_KEY')
model_name = ''
llm = DeepSeekChatModel("deepseek-r1:latest", None, "http://localhost:11434/api/chat", "ollama")

# 初始化 Agent
system_message = "你是一个知识渊博的助手"
bot = DeepSeekAssistant(llm=llm, system_message=system_message)

# 初始化 RAG 工具
rag_tool = RAGTool(llm=llm)

# 向数据存储模块添加文档
add_document("中国的一线城市有北京、上海、广州和深圳。")
add_document("北京是中国的首都，也是政治和文化中心。")
add_document("上海是中国的经济中心，拥有众多的金融机构。")

# 定义用户消息
query = "中国一线城市的特点是什么"
messages = [{"role": "user", "content": query}]

# 使用 RAG 工具处理用户消息
result = rag_tool.call({"query": query})
print(f"用户查询: {query}")
print(f"RAG 工具回答: {result}")