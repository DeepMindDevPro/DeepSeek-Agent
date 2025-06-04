# deepseek_agent/interaction/router.py（新增路由模块）
import spacy

class Router:
    def __init__(self):
        self.nlp = spacy.load("zh_core_web_sm")  # 中文意图识别模型

    def get_agent(self, user_query: str) -> str:
        doc = self.nlp(user_query)
        if any(token.text in ["代码", "编程", "调试"] for token in doc):
            return "coder_agent"
        elif any(token.text in ["搜索", "网页", "新闻"] for token in doc):
            return "browser_agent"
        else:
            return "default_agent"