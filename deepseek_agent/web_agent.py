class WebAgent:
    """智能网页浏览代理（添加 name 属性）"""
    capabilities = ["web_search", "info_extraction", "form_submit"]

    def __init__(self, llm_provider):
        self.name = "WebAgent"  # 显式定义 name 属性
        self.llm = llm_provider
        self.browser = self._init_browser()  # 初始化无头浏览器

    # 其他方法保持不变
    def _init_browser(self):
        from selenium.webdriver import Chrome
        from selenium.webdriver.chrome.options import Options
        options = Options()
        return Chrome(options=options)

    def execute(self, task: dict) -> str:
        prompt = f"""需要完成以下网页操作：{task['description']}
        请生成具体的浏览器操作步骤（用JSON格式返回）"""
        steps = self.llm.generate(prompt)
        return self._execute_steps(steps)

    def _execute_steps(self, steps):
        # 步骤执行逻辑（示例，需根据实际需求实现）
        return f"执行网页操作步骤: {steps}"