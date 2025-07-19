import logging

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator, Optional, Callable
from google.genai import types

from . import intent_recognition_prompt
from one_agent.app.config import ModelConfig

# 移除直接导入
# from .cot_task_agent import cot_task_agent
# from .knowledge_search_agent import knowledge_search_agent
# from .task_execute_agent import task_execute_agent


# 定义意图输出schema
class IntentOutput(BaseModel):
    intent: str = Field(description="intent type.")
    slot: list[str] = Field(description="slot type.")


intention_recognition = LlmAgent(
    name="IntentionRecognition",
    model=LiteLlm(model=ModelConfig.GENERAL_MODEL, response_format=IntentOutput),
    instruction=intent_recognition_prompt.PROMPT,
    description="根据意图识别调用不同的agent",
    output_schema=IntentOutput,
    output_key="intent_output",
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)


# 延迟加载子代理函数
def _get_task_execute_agent():
    from .task_execute_agent import task_execute_agent
    return task_execute_agent


def _get_knowledge_search_agent():
    from .knowledge_search_agent import knowledge_search_agent
    return knowledge_search_agent


def _get_cot_task_agent():
    from .cot_task_agent import cot_task_agent
    return cot_task_agent


# 新的IntentRouter类集成意图识别和路由功能
def _route_to_agent(intent) -> Optional[Callable]:
    """
    根据意图路由到对应的子代理（内部方法）

    Args:
        intent: 意图识别结果

    Returns:
        获取对应子代理的函数
    """
    intent_to_agent_getter = {
        "normal_search": _get_task_execute_agent,
        "knowledge_search": _get_knowledge_search_agent,
        "agent_search": _get_cot_task_agent,
        "reject_search": None  # 拒绝处理的情况
    }

    return intent_to_agent_getter.get(intent, None)


class IntentRouter(BaseAgent):
    """集成意图识别和路由功能的代理类"""
    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        实现意图识别和路由逻辑
        
        Args:
            ctx: 调用上下文
            
        Returns:
            事件生成器
        """
        # 1. 运行意图识别
        async for event in intention_recognition.run_async(ctx):
            yield event

        # 2. 获取意图结果并路由
        intent_output = ctx.session.state.get("intent_output")
        question = ctx.session.state.get("question", "")
        logging.info("[IntentRouter] question: %s, intent_output: %s", question, intent_output)
        if not intent_output:
            # 如果没有识别出意图，返回错误信息
            error_message = "无法识别意图，请重新描述您的请求。"
            yield Event(
                author=self.name,
                content=types.Content(
                    parts=[types.Part(text=error_message)]
                )
            )
            return
        intent = intent_output["intent"]
        # 3. 路由到相应的子代理
        agent_getter = _route_to_agent(intent)
        if not agent_getter:
            # 如果没有匹配的代理（例如拒绝请求的情况）
            reject_message = "抱歉，您的请求超出了我的处理范围."
            yield Event(
                author=self.name,
                content=types.Content(
                    parts=[types.Part(text=reject_message)]
                )
            )
            return

        # 4. 获取并运行目标子代理
        target_agent = agent_getter()
        async for event in target_agent.run_async(ctx):
            yield event


# 实例化IntentRouter
intent_router_agent = IntentRouter(
    name="IntentRouter",
    description="根据意图识别并路由到相应的专业代理",
)
