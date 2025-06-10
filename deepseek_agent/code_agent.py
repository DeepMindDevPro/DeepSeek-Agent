class CodeAgent:
    """代码生成与调试代理"""
    capabilities = ["code_generation", "debugging", "unit_test"]

    def __init__(self, llm_provider):
        self.llm = llm_provider
        self.languages = ["python", "go", "java"]  # 支持语言

    def execute(self, task: dict) -> str:
        prompt = f"""需要编写{task['language']}代码实现：{task['description']}
        要求：包含注释、错误处理、示例用法"""
        code = self.llm.generate(prompt)
        # 附加调试逻辑（可选）
        return self._debug_code(code)