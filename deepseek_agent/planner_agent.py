from typing import List, Dict, Optional
import logging
from collections.abc import Iterator  # 从collections.abc导入（Python 3.9+）
from deepseek_agent.agent import Agent  # 继承基础Agent类（参考架构中的agents/agent.py）
from deepseek_scheduler.agent_registry import AgentRegistry  # 代理注册中心
from deepseek_llm_provider.base_provider import BaseLLMProvider  # LLM基础接口

class PlannerAgent(Agent):
    def __init__(
        self,
        name: str,
        prompt_path: str,
        llm_provider: BaseLLMProvider,
        agent_registry: AgentRegistry,
        verbose: bool = False
    ):
        """
        任务规划代理初始化（修正父类参数调用）
        """
        # 调用父类Agent的__init__（传递3个参数：function_list, llm, system_message）
        super().__init__(
            function_list=None,  # 无工具列表时传None
            llm=llm_provider,    # LLM提供器传递给父类的llm参数
            system_message=None  # 无系统提示时传None
        )
        # 子类特有属性
        self.name = name
        self.prompt_path = prompt_path
        self.agent_registry = agent_registry
        self.verbose = verbose
        self.supported_agents = ["Web", "Coder", "File", "Casual"]
        #日志处理
        self.logger = logging.getLogger(f"PlannerAgent.{self.name}")
        # 根据verbose参数设置日志级别（verbose为True时输出INFO及以上日志）
        self.logger.setLevel(logging.INFO if verbose else logging.WARNING)
        # 可选：添加控制台处理器（若项目未全局配置日志）
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        self._load_prompt_template()


    def _load_prompt_template(self) -> None:
        """加载提示词模板（从文件读取，示例见prompts/base/planner_agent_en.txt）"""
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()
            self.logger.info(f"prompt_template: {self.prompt_template}")

    def _build_planning_prompt(self, user_task: str) -> str:
        """构造LLM输入提示词（转换代理列表为字符串，修正占位符匹配）"""
        # 动态获取可用代理列表并转换为字符串（如 "Web, Coder, File, Casual"）
        available_agents = self.agent_registry.get_available_agents()

        # 示例任务分解（硬编码示例，不包含占位符）
        example = """
    示例任务: "制作Python天气应用"
    输出计划:
    [
        {"agent": "Web", "id": "1", "need": [], "task": "搜索可用的天气API"},
        {"agent": "Web", "id": "2", "need": ["1"], "task": "申请天气API的API Key"},
        {"agent": "File", "id": "3", "need": ["2"], "task": "创建项目目录结构"},
        {"agent": "Coder", "id": "4", "need": ["3"], "task": "编写Python天气应用代码"}
    ]
            """

        # 构造完整提示词（传递字符串类型的available_agents）
        return self.prompt_template.format(
            available_agents=available_agents,
            user_task=user_task,
            example=example
        )


    def generate_task_plan(self, user_task: str) -> Optional[List[Dict]]:
        """
        生成结构化任务计划
        :param user_task: 用户原始任务
        :return: 任务计划列表（每个元素包含agent、id、need、task）
        """
        # 1. 构造LLM输入提示词
        prompt = self._build_planning_prompt(user_task)
        # 2. 调用LLM生成计划（通过LLM提供器的generate方法）
        llm_response = self.llm.generate([{"role": "user", "content": prompt}])
        # 3. 解析并验证LLM输出（确保符合JSON格式）
        try:
            plan = self._parse_llm_response(llm_response)
            return self._validate_plan(plan)
        except Exception as e:
            self.logger.error(f"任务计划生成失败: {str(e)}")
            return None


    def _parse_llm_response(self, response: str) -> List[Dict]:
        """解析LLM返回的非结构化文本，提取JSON格式的任务计划"""
        # 实际实现中需处理LLM的非严格输出（如多余文本包裹）
        # 示例：从LLM返回的"```json\n...\n```"中提取JSON
        start = response.find("```json") + len("```json")
        end = response.find("```", start)
        json_str = response[start:end].strip()
        return eval(json_str)  # 实际推荐使用json.loads()，此处为简化示例


    def _validate_plan(self, plan: List[Dict]) -> List[Dict]:
        """验证任务计划格式和逻辑有效性"""
        required_fields = ["agent", "id", "need", "task"]
        for task in plan:
            # 检查字段完整性
            if not all(field in task for field in required_fields):
                raise ValueError(f"任务 {task.get('id')} 缺少必要字段: {required_fields}")
            # 检查代理是否存在
            if task["agent"] not in self.supported_agents:
                raise ValueError(f"未知代理类型: {task['agent']}")
            # 检查依赖ID是否已定义（需保证前置任务存在）
            for need_id in task["need"]:
                if not any(t["id"] == need_id for t in plan):
                    raise ValueError(f"任务 {task['id']} 依赖的ID {need_id} 未定义")
        return plan


    def execute(self, user_task: str) -> List[Dict]:
        """主执行入口（生成并返回任务计划）"""
        self.logger.info(f"开始规划任务: {user_task}")
        plan = self.generate_task_plan(user_task)
        if plan:
            self.logger.info(f"任务计划生成成功: {plan}")
        else:
            self.logger.error("任务计划生成失败")
        return plan


    def _run(self, messages: List[Dict], lang: str = 'en', **kwargs) -> Iterator[List[Dict]]:
        """实现父类抽象方法_run（符合Agent类定义）"""
        user_task = messages[-1]["content"]
        self.logger.info(f"开始规划任务: {user_task}")
        plan = self.generate_task_plan(user_task)
        if plan:
            self.logger.info(f"任务计划生成成功: {plan}")
            # 将计划转换为Agent类所需的消息格式
            yield [{"role": "assistant", "content": f"任务计划已生成: {plan}"}]
        else:
            self.logger.error("任务计划生成失败")
            yield [{"role": "assistant", "content": "任务计划生成失败"}]