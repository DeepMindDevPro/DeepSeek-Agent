# planner_test.py（示例）
from deepseek_llm_provider.ollama import OllamaProvider
from deepseek_agent.planner_agent import PlannerAgent
from deepseek_scheduler.agent_registry import AgentRegistry

from deepseek_agent.web_agent import WebAgent  # 假设存在WebAgent类

# 配置Ollama服务
config = {
    "provider_model": "deepseek-r1:32b",
    "provider_server_address": "localhost:11434"
}

llm_provider = OllamaProvider(config)
agent_registry = AgentRegistry()

# 注册代理（关键：否则available_agents为空）
web_agent = WebAgent(llm_provider=llm_provider)
agent_registry.register(web_agent)

planner = PlannerAgent(
    name="Planner",
    prompt_path="/Users/gechunfa1/Documents/ai/DeepSeek-Agent/prompts/planner_agent_zh.txt",
    llm_provider=llm_provider,
    agent_registry=agent_registry,
    verbose=True
)

# 生成任务计划（正常执行）
user_task = "制作一个自动生成周报的Python脚本，并保存为PDF"
task_plan = planner.execute(user_task)
print("任务计划:", task_plan)