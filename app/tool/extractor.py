import os
import re

import pandas as pd
from mysql.connector import InterfaceError

import re
import sqlparse


def extract_sql_queries(markdown_text):
    # 正则匹配所有 SQL 代码块
    sql_blocks = re.findall(r'```sql\n(.*?)```', markdown_text, re.DOTALL)

    queries = []
    for block in sql_blocks:
        # 清除注释和空行
        cleaned = '\n'.join([
            line.split('--')[0].strip()  # 移除行内注释
            for line in block.split('\n')
            if line.strip() and not line.strip().startswith('--')
        ])

        # 分割独立语句并验证类型
        for statement in sqlparse.split(cleaned):
            parsed = sqlparse.parse(statement)[0]
            if parsed.get_type() in 'SELECT':
                queries.append(statement.strip() + ';')  # 补充分号

    return queries

def execute_mysql_and_save_to_csv(sql, conn, output_csv_path):
    # 创建数据库连接
    cursor = conn.cursor()

    # 执行 SQL 语句并获取结果
    cursor.execute(sql)
    try:
        result = cursor.fetchall()
    except InterfaceError as e:
        print(f"Error executing SQL: {e}")
        return ''

    if not result:
        print("No results found.")
        return ''
    # 获取列名
    column_names = [description[0] for description in cursor.description]

    # 将结果转换为 DataFrame
    df = pd.DataFrame(result, columns=column_names)

    # 将 DataFrame 保存为 CSV 文件
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False, mode='w', header=True)
    return df.to_csv(None, index=False)
