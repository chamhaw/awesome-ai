from google.adk.agents import LlmAgent, BaseAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator

from google.genai import types
from pydantic import BaseModel, Field

from one_agent.app.agents.base.state_update_agent import StateUpdateAgent
from one_agent.app.config import ModelConfig

PROMPT = """

You are an experienced data product manager specializing in data requirements. Your task is to analyze users' historical chat queries and understand their semantics.

You have three possible actions. You must select one of the following intents:

<intent>
- original_problem: If the current question has no semantic relationship with the previous conversation, input the current question directly without rewriting it.
- ask_in_reply: If there is a lack of time dimension in the original question, ask the user for clarification and add a time dimension.
- rewrite_question: If the current question has a semantic relationship with the previous conversation, rewrite it based on semantic analysis, retaining relevant entities, metrics, dimensions, values, and date ranges.
</intent>

strictly follows the provided Guidelines for this task:

<guideline>
- The output language should be consistent with the language of the question.
- Only output a JSON structure, where the only keys are "intent" and "query" and do not output any other text, symbols, or explanations;.
</guideline>

Examples will follow, where in the chat history, "User" represents the user's question, and "Assistant" represents the chatbot's answer.

<example>

<example_one>
The Chat history is :
user: 上个月欧洲希尔顿酒店的销量是多少
assistant: 查询上个月欧洲希尔顿酒店的销量
user: 亚洲呢
assistant: 查询上个月亚洲希尔顿酒店的销量
user: 上上个月呢

answer:

{
    "intent" : "rewrite_question",
    "query": "查询上上个月亚洲希尔顿酒店的销量"
}
</example_one>

<example_two>
The Chat history is :
user: 上个月欧洲希尔顿酒店的销量是多少。
assistant: 查询上个月欧洲希尔顿酒店的销量。

The user question is : 对比欧洲和亚洲两个的订单量

answer:

{
    "intent" : "original_problem",
    "query": "对比欧洲和亚洲两个的订单量"
}
</example_two>

<example_three>
The user question is : 查询万豪酒店的订单量

answer:

{
    "intent" : "ask_in_reply",
    "query": "请问您想查询的时间范围是多少呢"
}
</example_three>

<example>

The Chat History:
{chat_history_text}
========================
The question is : {question}

"""


class RewriteQueryOutput(BaseModel):
    intent: str = Field(..., title="intent")
    query: str = Field(..., title="query")


# 原始的LlmAgent定义
raw_rewrite_query_agent = LlmAgent(
    name="raw_rewrite_query_agent",
    model=LiteLlm(model=ModelConfig.GENERAL_MODEL, temperature=0.1),
    instruction=PROMPT,
    description="判断问题的必要信息是否充分，并重写问题",
    output_schema=RewriteQueryOutput,
    output_key="rewrite_query",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)


# 新的包装类，用于处理intent=ask_in_reply的情况
class RewriteQueryAgentWrapper(StateUpdateAgent):
    """包装RewriteQueryAgent，处理intent=ask_in_reply的情况"""

    llm_agent: LlmAgent = raw_rewrite_query_agent

    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        实现代理运行逻辑
        
        Args:
            ctx: 调用上下文
            
        Returns:
            事件生成器
        """
        # 运行原始LLM代理
        async for event in self.llm_agent.run_async(ctx):
            yield event

        # 检查结果
        rewrite_query = ctx.session.state.get("rewrite_query")
        if rewrite_query and rewrite_query.get("intent") == "ask_in_reply":
            # 如果intent是ask_in_reply，直接返回query并终止对话
            event = Event(
                author=self.name,
                content=types.Content(
                    parts=[types.Part(text=rewrite_query.get("query"))]
                )
            )
            event.actions.skip_summarization = True
            event.actions.escalate = True
            yield event
        elif rewrite_query :
            yield self.update_state({
                "question": rewrite_query.get("query"),
            })
        # 其他情况继续正常处理
        return


# 使用包装后的代理
rewrite_query_agent = RewriteQueryAgentWrapper(
    name="query_rewrite_agent",
    description="问题重写，判断问题是否清晰，并处理需要用户澄清的情况"
)
