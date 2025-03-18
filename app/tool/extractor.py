import re

import pandas as pd


def extract_sql_from_markdown(markdown_text):
    # 正则表达式匹配 Markdown 中的代码块
    code_blocks = re.findall(r'```sql(.*?)```', markdown_text, re.DOTALL)
    sql_statements = [block.strip() for block in code_blocks]
    return sql_statements

def execute_sql_and_save_to_csv(sql, conn, output_csv_path):
    # 创建数据库连接
    cursor = conn.cursor()

    # 执行 SQL 语句并获取结果
    cursor.execute(sql)
    result = cursor.fetchall()

    # 获取列名
    column_names = [description[0] for description in cursor.description]

    # 将结果转换为 DataFrame
    df = pd.DataFrame(result, columns=column_names)

    # 将 DataFrame 保存为 CSV 文件
    df.to_csv(output_csv_path, index=False, mode='a', header=not pd.io.common.file_exists(output_csv_path))
