from typing import List, Optional


class AgentRegistry:
    """代理注册中心（补充get_available_agents方法）"""

    def __init__(self):
        self.agents = {}  # {agent_name: agent_instance}
        self.capabilities = {}  # {capability: agent_name}

    def register(self, agent):
        """注册代理及其能力（调整为以代理名称为键）"""
        agent_name = agent.name  # 假设代理有name属性
        self.agents[agent_name] = agent
        for cap in agent.capabilities:
            self.capabilities[cap] = agent_name

    def get_available_agents(self) -> List[str]:
        """返回所有已注册的代理名称列表"""
        return list(self.agents.keys())

    def get_agent_by_capability(self, capability: str) -> Optional[str]:
        """根据能力获取对应的代理名称"""
        return self.capabilities.get(capability)