# scheduler/router.py
class TaskRouter:
    """智能任务路由"""

    def __init__(self, agent_registry, llm_provider):
        self.registry = agent_registry
        self.llm = llm_provider  # 用于任务分析

    def route(self, task: dict) -> object:
        """动态选择最佳代理"""
        # 1. 分析任务类型
        prompt = f"""分析以下任务需要的能力（返回逗号分隔的能力标签）：
        任务描述：{task['description']}
        可用能力：{list(self.registry.agents.keys())}"""
        required_caps = self.llm.generate(prompt).split(',')

        # 2. 匹配代理（支持多能力组合）
        matched_agents = [self.registry.agents[cap] for cap in required_caps
                          if cap in self.registry.agents]

        if not matched_agents:
            raise ValueError("无可用代理处理该任务")

        # 3. 选择优先级最高的代理（可扩展权重算法）
        return matched_agents[0]