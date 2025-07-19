from typing import AsyncGenerator, Dict, List, Any, Tuple

from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from one_agent.app.agents.base.state_update_agent import StateUpdateAgent


def _convert_to_markdown_table(sql_result: Tuple[List[Dict[str, Any]], List[str]]) -> str:
    """将SQL执行结果转换为Markdown表格格式

    Args:
        sql_result: SQL执行结果数据，是一个元组 (rows, columns)
            rows: 数据行的列表，每行是一个字典
            columns: 列名的列表

    Returns:
        Markdown表格格式的字符串
    """
    if not sql_result or len(sql_result) != 2:
        return "无有效数据可展示"

    rows, columns = sql_result

    if not columns or not rows:
        return "无有效数据可展示"

    # 创建表头
    header = " | ".join(columns)
    # 创建分隔行
    separator = " | ".join(["---"] * len(columns))

    # 创建数据行
    data_rows = []
    for row in rows:
        # 从每行的字典中按顺序提取列值
        row_values = []
        for col in columns:
            value = row.get(col, "")
            # 确保值是字符串
            row_values.append(str(value) if value is not None else "")
        data_rows.append(" | ".join(row_values))

    # 组合成完整的Markdown表格
    markdown_table = f"| {header} |\n| {separator} |\n"
    markdown_table += "\n".join([f"| {row} |" for row in data_rows])

    return markdown_table


class DataVisualizeAgent(StateUpdateAgent):

    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        if "sql_execute_result" not in ctx.session.state:
            raise Exception("sql_execute_result not found")
        
        # 获取SQL执行结果
        sql_result = ctx.session.state["sql_execute_result"]
        
        # 将SQL结果转换为Markdown表格
        markdown_table = _convert_to_markdown_table(sql_result)
        
        result_event = Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=types.Content(
                role='model',
                parts=[types.Part.from_text(text=markdown_table)],
            ),
        )
        yield result_event


visualize_agent = DataVisualizeAgent(
    name="DataVisualizeAgent",
)