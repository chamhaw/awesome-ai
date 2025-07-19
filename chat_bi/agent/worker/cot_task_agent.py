import json
import logging
import uuid
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional, List, Tuple, Set

from google.adk import Runner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.sessions import InMemorySessionService
from google.genai import types

from one_agent.app.agents.base.state_update_agent import StateUpdateAgent
from one_agent.app.agents.bi_assistant.sub_agents.cot_sub_task_agent import cot_sub_task_agent
from one_agent.app.agents.bi_assistant.sub_agents.data_analysis_agent import data_analysis_agent
from one_agent.app.agents.bi_assistant.sub_agents.cot_task_split_agent import cot_task_split_agent
from one_agent.app.agents.bi_assistant.sub_agents.retriever import cot_retrieve_search, table_schema_retrieve

SUB_TASK_APP = "sub_task_app"
SUB_TASK_USER_ID = "sub_task_user_id"


class CotTaskAgent(StateUpdateAgent):

    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        rewrite_query = ctx.session.state.get("rewrite_query")
        if "query" in rewrite_query:
            question = rewrite_query["query"]
        else:
            question = ctx.session.state.get("question")
        yield self.update_state({
            "rewrite_question": question,
        }, ctx)
        cot_retrieves = cot_retrieve_search(question)
        table_schema = table_schema_retrieve()
        table_schema_data = "\n".join(table_schema)
        cot_knowledge = "\n".join(cot_retrieves)
        # 使用update_state方法更新状态
        yield self.update_state({
            "cot_knowledge": cot_knowledge,
            "table_schema_data": table_schema_data,
            "sql_guidance": "",
        }, ctx)

        async for event in cot_task_split_agent.run_async(ctx):
            yield event

        if "cot_task_split_output" not in ctx.session.state:
            raise Exception("cot_task_split_output is missing")

        sub_tasks = ctx.session.state["cot_task_split_output"]["sub_tasks"]
        data_analyse_result = []

        # 准备上下文数据字典，用于传递给协程
        ctx_data = {
            "table_schema_data": ctx.session.state.get("table_schema_data", ""),
            "cot_knowledge": ctx.session.state.get("cot_knowledge", ""),
        }

        # 准备所有子任务协程
        subtask_coroutines = []
        for name, step in sub_tasks.items():
            # 为每个子任务创建一个协程
            coroutine = self.process_subtask(ctx, step, name, ctx_data)
            subtask_coroutines.append(coroutine)

        # 并行执行所有子任务协程
        # subtask_results = await asyncio.gather(*subtask_coroutines)
        subtask_results = [await subtask for subtask in subtask_coroutines]

        # 处理所有子任务的结果和事件
        for subtask_data in subtask_results:
            # 处理子任务的结果
            data_analyse_result.append(subtask_data)

        logging.info(f"sub_tasks_execute_data: {data_analyse_result}")

        yield self.update_state({
            "sub_tasks_execute_data": json.dumps(data_analyse_result, ensure_ascii=False),
        }, ctx)

        async for event in data_analysis_agent.run_async(ctx):
            yield event

    async def process_subtask(self, parent_context: InvocationContext, step: str, task_name: str,
                              ctx_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个子任务的协程函数

        Args:
            parent_context:
            step: 子任务的问题或查询
            task_name: 子任务名称
            ctx_data: 原始上下文中需要共享的数据

        Returns:
            子任务处理结果和生成的事件
        """
        # 为每个子任务创建一个唯一的session_id
        sub_task_session_id = f"subtask_{uuid.uuid4().hex}"

        # 创建一个新的会话
        session = parent_context.session_service.create_session(
            app_name=SUB_TASK_APP,
            user_id=SUB_TASK_USER_ID,
            session_id=sub_task_session_id
        )

        # 设置初始状态
        state_data = {
            "question": step,
            "chat_history": [],  # 清空聊天历史
            "table_schema_data": ctx_data.get("table_schema_data", ""),
            "cot_knowledge": ctx_data.get("cot_knowledge", ""),
        }
        parent_context.session_service.append_event(session, Event(author=self.name,
                                                                   actions=EventActions(state_delta=state_data)))

        # 创建Runner
        runner = Runner(
            agent=cot_sub_task_agent,
            app_name=SUB_TASK_APP,
            session_service=parent_context.session_service,
        )

        # 准备用户消息
        content = types.Content(
            role="user",
            parts=[types.Part(text=step)]
        )

        # 使用Runner执行agent，确保上下文完全隔离
        async for event in runner.run_async(
                user_id=SUB_TASK_USER_ID,
                session_id=sub_task_session_id,
                new_message=content
        ):
            pass

        # 从会话中获取结果
        session_state = parent_context.session_service.get_session(
            app_name=SUB_TASK_APP,
            user_id=SUB_TASK_USER_ID,
            session_id=sub_task_session_id).state

        sql_execute_result = session_state.get("sql_execute_result")
        sql = session_state.get("sql_query", "")

        # 准备结果数据
        result = None
        if sql_execute_result:
            result = {
                "task_name": task_name,
                "task_content": step,
                "sql_query": sql,
                "query_result": sql_execute_result,
            }

        # 返回任务结果和收集的事件
        return result


cot_task_agent = CotTaskAgent(
    name="cot_task_agent",
    description="Cot Task Agent",
)
