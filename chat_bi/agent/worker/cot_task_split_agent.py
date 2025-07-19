from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from pydantic import BaseModel, Field

from one_agent.app.config import ModelConfig

# 定义链式思考输出schema
class CotTaskSplitOutput(BaseModel):
    sub_tasks: dict[str, str] = Field(description="sub tasks of solving the problem")

# 定义链式思考代理提示词
COT_PROMPT = """

you are a data analysis expert as well as a retail expert. 

Your task is to conduct attribution analysis on the current problem, which requires breaking it down into multiple related sub problems.

Here is DDL of the database you are working on:

<table_schema>

{table_schema_data}

</table_schema>

Here are some guidelines you should follow:

<guidelines>

{sql_guidance}

- Please focus on the business knowledge in the examples, If the problem occurs in the example, please use the sub-problems in the exampl

- only output the JSON structure

Here are some chain of thought you should follow:

<cot>
{cot_knowledge}}
</cot>

Finally only output the JSON structure without outputting any other content and with limitation: 
1. json format: 
{
    "problem":"xx"
    "sub_tasks":{
        "task_1": "xxx",
        "task_2": "xxx",
        "task_3": "xxx",
        ...
        "task_n": "xxx",
    }
}
2. each subtask must have time slot

Here are some examples of breaking down complex problems into subtasks, You must focus on the following examples:

<examples>
input："请分析下2007年销售下降的原因？"
output:
{
    "problem":"请分析下2007年销售下降的原因？
    "sub_tasks":{
        "task_1": "分析2007年每月的销售总额和订单数量",
        "task_2": "分析2007年热销产品的销售情况",
        "task_3": "分析2007年不同客户类型的购买情况",
        "task_4": "分析2007年不同地区的销售表现",
        "task_5": "分析2007年促销活动对销售的影响"
    }
}

</examples>

</guidelines> 


The user question is : {rewrite_question}
"""


# 创建链式思考代理
cot_task_split_agent = LlmAgent(
    name="ChainOfThought",
    model=LiteLlm(model=ModelConfig.GENERAL_MODEL),
    instruction=COT_PROMPT,
    generate_content_config= types.GenerateContentConfig(
        temperature=0.1, # More deterministic output
    ),
    description="根据业务规则和领域知识拆解问题成多个子任务",
    output_schema=CotTaskSplitOutput,
    output_key="cot_task_split_output",
)
