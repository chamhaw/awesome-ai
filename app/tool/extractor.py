import re

def extract_sql_from_markdown(markdown_text):
    # 正则表达式匹配 Markdown 中的代码块
    code_blocks = re.findall(r'```sql(.*?)```', markdown_text, re.DOTALL)
    sql_statements = [block.strip() for block in code_blocks]
    return sql_statements
