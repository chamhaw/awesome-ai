from typing import Optional, AsyncGenerator

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from one_agent.app.agents.base.state_update_agent import StateUpdateAgent
from one_agent.app.agents.bi_assistant.sub_agents.retriever import entity_retrieve_search, qa_retrieve_search, \
    table_schema_retrieve_search
from one_agent.app.agents.bi_assistant.sub_agents.text2sql_agent import TextToSQLAgent
from one_agent.app.agents.bi_assistant.tools.sql_executor import sql_executor


def setup_entity_retrieval(
        callback_context: CallbackContext,
) -> Optional[types.Content]:
    intent_output = callback_context.state.get("intent_output", {})
    entity_slots = intent_output.get("slot", [])
    if not entity_slots:
        entity_slots = callback_context.state.get("entity_slots", [])
    normal_search_entity_slot = entity_retrieve_search(entity_slots)
    normal_search_qa_retrival = qa_retrieve_search(entity_slots)
    table_schema = table_schema_retrieve_search(entity_slots)
    callback_context.state["ner_example"] = normal_search_entity_slot
    callback_context.state["sql_examples"] = normal_search_qa_retrival
    callback_context.state["sql_schema"] = table_schema
    print("entity_slots:", entity_slots)
    print("ner_example:", normal_search_entity_slot)
    print("sql_examples:", normal_search_qa_retrival)
    print("sql_schema:", normal_search_entity_slot)


class TaskExecuteAgent(StateUpdateAgent):

    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        async for event in TextToSQLAgent.run_async(ctx):
            yield event

        if "sql_query" not in ctx.session.state:
            raise Exception("sql_query not found")
        sql_query = ctx.session.state["sql_query"]
        sql = sql_query.get("sql", "")
        generate_success = sql_query.get("success", False)
        if not generate_success:
            reason = sql_query.get("reason", "Something went wrong")
            yield self.update_state({'sql_execute_result': "sql is failed to generate with reason:" + reason}, ctx)
            return
        # 如果执行异常，再用TextToSQLAgent生成一次sql
        try:
            sql_execute_result = sql_executor.execute_query(sql)
        except Exception as e:
            async for event in TextToSQLAgent.run_async(ctx):
                yield event
            if "sql_query" not in ctx.session.state:
                raise Exception("sql_query not found")
            sql_query = ctx.session.state["sql_query"]
            sql = sql_query.get("sql")
            try:
                sql_execute_result = sql_executor.execute_query(sql)
            except Exception as e:
                yield self.update_state({'sql_execute_result': "some wrong when execute sql=" + sql}, ctx)
                return

        if sql_execute_result:
            yield self.update_state({'sql_execute_result': sql_execute_result}, ctx)
        else:
            raise Exception("sql_execute_result not found")


task_execute_agent = TaskExecuteAgent(
    name="task_execute_agent",
    before_agent_callback=setup_entity_retrieval
)
