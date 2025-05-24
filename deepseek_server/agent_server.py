# agent server
# 示例：在DeepSeek-Agent项目中创建一个Flask API服务
from flask import Flask, request, jsonify
from deepseek_agent.model import DeepSeekChatModel
from deepseek_agent.assistant import DeepSeekAssistant
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

app = Flask(__name__)

# 初始化DeepSeek模型
api_key = os.getenv('DEEPSEEK_API_KEY')
model_name = 'deepseek-r1:latest'
llm = DeepSeekChatModel(model_name, None, "http://localhost:11434/api/chat", "ollama")

# 初始化Agent
system_message = "你是一个知识渊博的助手"
bot = DeepSeekAssistant(llm=llm, system_message=system_message)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
    response = []
    for rsp in bot.run(messages):
        response.extend(rsp)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)