from flask import Flask, request, jsonify
from deepseek_agent.model import DeepSeekChatModel
from deepseek_agent.assistant import DeepSeekAssistant
import os
from dotenv import load_dotenv
from flask_cors import CORS
import re

# 加载.env文件
load_dotenv()

app = Flask(__name__)
CORS(app)  # 解决跨域问题

# 初始化DeepSeek模型
api_key = os.getenv('DEEPSEEK_API_KEY')
model_name = 'deepseek-r1:latest'
llm = DeepSeekChatModel(model_name, None, "http://localhost:11434/api/chat", "ollama")

# 初始化Agent
system_message = "你是一个知识渊博的助手"
bot = DeepSeekAssistant(llm=llm, system_message=system_message)

@app.route('/api/chat', methods=['POST'])
def chat():
    # 获取请求中的JSON数据
    data = request.get_json()
    if data is None:
        return jsonify({"error": "请求中缺少有效的JSON数据"}), 400

    # 提取消息列表
    messages = data.get('messages', [])
    if not isinstance(messages, list):
        return jsonify({"error": "消息数据格式必须为列表"}), 400

    response = []
    # 运行Agent获取响应
    for rsp in bot.run(messages):
        response.extend(rsp)

    final_response = []
    # 解析思维链和正式答案
    for res in response:
        try:
            # 直接从res中获取content
            content = res["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            print(f"解析响应数据时出错: {e}, 响应数据: {res}")
            return jsonify({"error": "响应数据格式不正确"}), 500

        think_pattern = r'<think>(.*?)</think>'
        think_match = re.search(think_pattern, content, re.DOTALL)

        if think_match:
            think_content = think_match.group(1)
            answer_content = content.replace(think_match.group(0), '').strip()
        else:
            think_content = ""
            answer_content = content

        final_response.append({
            "choices": [
                {
                    "message": {
                        "content": answer_content,
                        "role": "assistant"
                    },
                    "think_content": think_content
                }
            ]
        })
    return jsonify(final_response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)