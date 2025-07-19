import logging
from typing import AsyncGenerator

from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from one_agent.app.agents.base.state_update_agent import StateUpdateAgent
from one_agent.app.agents.bi_assistant.sub_agents.intent_recognition_agent import intention_recognition
from one_agent.app.agents.bi_assistant.sub_agents.task_execute_agent import TaskExecuteAgent, task_execute_agent


class CotSubTaskExecuteAgent(StateUpdateAgent):

    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # 1. 运行意图识别
        async for event in intention_recognition.run_async(ctx):
            yield event

        # 2. 获取意图结果并路由
        intent_output = ctx.session.state.get("intent_output")
        question = ctx.session.state.get("question")
        logging.info("[CotSubTaskExecuteAgent] question: %s, intent_output: %s", question, intent_output)
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
        async for event in task_execute_agent.run_async(ctx):
            yield event


cot_sub_task_agent=CotSubTaskExecuteAgent(
    name="cot_sub_task_agent",
)