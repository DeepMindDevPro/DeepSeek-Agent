import requests
import json
from typing import Optional, Dict, List, Generator

'''
ollama参考api地址: https://github.com/ollama/ollama/blob/main/docs/api.md
'''

class DeepSeekChatModel:
    def __init__(
            self,
            model_name: str,
            api_key: Optional[str] = None,
            api_url: Optional[str] = None,
            provider: str = "deepseek"  # 可选: "deepseek"（官方API）或 "ollama"
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.provider = provider.lower()

        # 设置默认API地址
        if provider == "deepseek":
            self.api_url = api_url or "https://api.deepseek.com/v1/chat/completions"
        elif provider == "ollama":
            self.api_url = api_url or "http://localhost:11434/api/chat"
        else:
            raise ValueError("provider参数仅支持deepseek或ollama")

    def chat(
            self,
            messages: List[Dict[str, str]],
            functions: Optional[List[Dict]] = None,
            stream: bool = False,
            extra_generate_cfg: Optional[Dict] = None,
    ) -> Generator[dict, None, None]:
        headers = {}
        request_data = {"model": self.model_name, "messages": messages, "stream": False}  # 强制设置stream=False

        # 处理不同提供商的参数
        if self.provider == "deepseek":
            if not self.api_key:
                raise ValueError("调用DeepSeek官方API需要提供api_key")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            request_data["functions"] = functions or []  # 官方API需显式传递函数列表
            if extra_generate_cfg:
                request_data.update(extra_generate_cfg)

        elif self.provider == "ollama":
            if functions:
                print("警告：Ollama不支持函数调用，functions参数将被忽略")
            if extra_generate_cfg:
                request_data.update(extra_generate_cfg)
            # 确保messages中的system提示为英文（覆盖传入的中文提示）
            # 此处强制设置为英文提示，若需要灵活控制，可移除该逻辑并由调用方传入正确格式
            request_data["messages"] = [
                # {"role": "system", "content": "你是一个中国历史、政治、文化、经济各方面的专家"},
                {"role": "system", "content": "你是一个知识渊博的助手."},
                *[msg for msg in messages if msg["role"] != "system"]  # 移除传入的system提示（如有）
            ]

        # 打印请求信息（调试用）
        print("\n=== 发送请求 ===")
        print(f"URL: {self.api_url}")
        print(request_data)
        print(f"参数: {json.dumps(request_data, indent=2)}")

        # 发起请求
        response = requests.post(
            self.api_url,
            headers=headers,
            json=request_data,
            stream=stream  # 实际请求的stream参数以request_data中的为准
        )

        # 处理响应状态码
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {e.response.status_code}, 响应内容: {e.response.text}")
            raise

        # 处理响应内容
        if stream:
            print('stream result')
            yield from self._handle_stream_response(response)
        else:
            print('no stream result')
            yield from self._handle_non_stream_response(response)

    def _handle_stream_response(self, response: requests.Response) -> Generator[dict, None, None]:
        """处理流式响应（适用于DeepSeek官方API和Ollama）"""
        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8").strip()
                if self.provider == "deepseek":
                    # DeepSeek官方API流式响应为JSONL格式
                    if line_str.startswith("data: "):
                        line_str = line_str[6:]
                    yield json.loads(line_str)
                elif self.provider == "ollama":
                    # Ollama流式响应为逐字符输出，需包装为delta格式
                    yield {"choices": [{"delta": {"content": line_str}}]}

    def _handle_non_stream_response(self, response: requests.Response) -> Generator[dict, None, None]:
        """处理非流式响应（适用于DeepSeek官方API和Ollama）"""
        response_text = response.text.strip()
        print(response_text)
        if self.provider == "deepseek":
            # 直接返回官方API的JSON响应
            yield response.json()
        elif self.provider == "ollama":
            # 从响应中提取首个有效JSON对象（处理可能的额外数据）
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start == -1 or end <= start:
                raise ValueError(f"Ollama响应中未找到有效JSON: {response_text}")
            valid_json = response_text[start:end]
            try:
                result = json.loads(valid_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"解析Ollama响应失败: {e}, 数据片段: {valid_json[:200]}...")

            # 适配Ollama的响应结构
            yield {
                "choices": [{
                    "message": {
                        "content": result.get("message", {}).get("content", ""),
                        "role": result.get("message", {}).get("role", "assistant")
                    }
                }]
            }


# ---------------------
# 使用示例（Ollama模式，强制设置英文system提示）
# ---------------------
if __name__ == "__main__":
    # 初始化Ollama模型（需提前启动ollama serve并拉取模型）
    llm = DeepSeekChatModel(
        model_name="deepseek-r1:latest",
        provider="ollama"
    )

    # 定义用户消息（即使传入中文system提示，代码中会强制替换为英文）
    messages = [
        {"role": "system", "content": "你是一个中国经济专家"},  # 会被代码移除并替换为英文
        {"role": "user", "content": "中国的一线城市有哪些"}
    ]

    # 调用模型（非流式，强制设置stream=False）
    for response in llm.chat(messages, stream=False):
        print("\n=== 模型响应 ===")
        print(response["choices"][0]["message"]["content"])