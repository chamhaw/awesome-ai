from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field

from one_agent.app.config import ModelConfig


# 定义知识搜索输出schema
class KnowledgeOutput(BaseModel):
    answer: str = Field(description="Answer to the knowledge query.")


# 定义知识搜索代理提示词
KNOWLEDGE_SEARCH_PROMPT = """
你是一个知识库查询专家。你需要回答用户关于系统、术语、缩写等相关问题。

当遇到你不确定的信息时，清楚地表明你不知道，而不是编造答案。
尽可能提供精确、简洁、有信息量的回答。

例如：
问题："什么是SQL？"
回答："SQL（Structured Query Language）是一种用于管理关系型数据库的编程语言，用于存储、操作和检索存储在关系型数据库中的数据。SQL通过使用声明性语句，允许用户描述他们想要从数据库中检索或修改的数据。"

问题："BMW是什么意思？"
回答："BMW（Bayerische Motoren Werke）是一家总部位于德国的高级汽车和摩托车制造商，成立于1916年。"
"""

# 创建知识搜索代理
knowledge_search_agent = LlmAgent(
    name="KnowledgeSearch",
    model=LiteLlm(model=ModelConfig.GENERAL_MODEL),
    instruction=KNOWLEDGE_SEARCH_PROMPT,
    description="回答用户关于知识、术语、缩写等问题",
    output_schema=KnowledgeOutput,
    output_key="knowledge_answer",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)
