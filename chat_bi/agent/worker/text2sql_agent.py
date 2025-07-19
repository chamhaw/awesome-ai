from typing import Optional, Dict, List, Any

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from pydantic import BaseModel, Field

from one_agent.app.config import ModelConfig
from one_agent.app.agents.bi_assistant.tools.sql_executor import SQLExecutor


# 定义Text2SQL代理提示词
TEXT2SQL_PROMPT = """
You are a data analysis expert and proficient in {dialect}.

{dialect_prompt}

Assume a database with the following tables and columns exists:

Given the following database schema, transform the following natural language requests into valid SQL queries.

<table_schema>

{sql_schema}

</table_schema>

Here are some examples of generated SQL using natural language.

<examples>

{examples}

</examples> 

Here are some ner info to help generate SQL.

<ner_info>

{ner_info}

</ner_info> 

You ALWAYS follow these guidelines when writing your response:

<guidelines>

When performing multi table association, if selecting the primary key, To prevent ambiguous columns, it is necessary to add a table name.

{sql_guidance}

</guidelines> 

Think about the sql question before continuing. If it's not about writing SQL statements, say 'Sorry, please ask something relating to querying tables'.

Think about your answer first before you respond.

if writing SQL statements, only output the JSON structure without outputting any other content, and with limitation:

<format>
{ "sql": "select * from xxx limit 1" }
<format>

<examples>
generate succeed:
{
    "sql": "select * from xxx limit 1",
    "success": true
}

generate failed:
{
    "sql": "select * from xxx limit 1",
    "success": false,
    "reason": "please ask something relating to querying tables"
}
</examples> 

The question is : {question}
"""

MYSQL_DIALECT_PROMPT = """You are a data analysis expert and proficient in MySQL. Given an input question, create a syntactically correct MySQL query to run.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {limit} results using the LIMIT clause as per MySQL. 
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
The table name does not require the use of backups (`). When generating SQL, do not add double quotes or single quotes around table names.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use CURDATE() function to get the current date, if the question involves "today". In the process of generating SQL statements, please do not use aliases. Aside from giving the SQL answer, concisely explain yourself after giving the answer
in the same language as the question."""

def setup_before_call(
        callback_context: CallbackContext,
) -> Optional[types.Content]:
    example_sql_prompt = ""
    example_ner_prompt = ""
    table_prompt = ""
    guidance_prompt = ""
    dialect_prompt = MYSQL_DIALECT_PROMPT.format(limit=100)
    for item in callback_context.state.get("sql_examples", []):
        example_sql_prompt += item +"\n"
    for item in callback_context.state.get("ner_example", []):
        example_ner_prompt += item +"\n"
    for item in callback_context.state.get("sql_schema", []):
        table_prompt += item +"\n"

    callback_context.state["dialect"] = "mysql"
    callback_context.state["dialect_prompt"] = dialect_prompt
    callback_context.state["sql_schema"] = table_prompt
    callback_context.state["sql_guidance"] = guidance_prompt
    callback_context.state["examples"] = example_sql_prompt
    callback_context.state["ner_info"] = example_ner_prompt

# 定义SQL输出schema
class SQLOutput(BaseModel):
    sql: str = Field(description="Generated SQL query.")
    success: bool = Field(description="Whether the sql was generated successfully.")
    reason: str = Field(description="The reason the sql can't be generated.")

# 创建Text2SQL代理
TextToSQLAgent = LlmAgent(
    name="TextToSQL",
    model=LiteLlm(model=ModelConfig.GENERAL_MODEL, response_format=SQLOutput),
    instruction=TEXT2SQL_PROMPT,
    generate_content_config= types.GenerateContentConfig(temperature=0.01),
    description="将自然语言查询转换为SQL查询",
    output_schema=SQLOutput,
    output_key="sql_query",
    before_agent_callback=setup_before_call,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)