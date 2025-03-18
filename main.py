from dotenv import load_dotenv
# 加载 .env 文件
load_dotenv()

from typing import List, Union

from llama_index.core.schema import NodeWithScore

from app import llm
from app.prompt import ddl
from app.tool import extractor
from app.llamaindex.indexer import retrieve
import mysql.connector


if __name__ == "__main__":
    data: List[NodeWithScore] = retrieve("test_index", """按照路线/路段/上下行/车道/路公司/管理中心/时间/数
    据来源/评价单元/指定起终点桩号(0-100),统计各项指标的均
    值、衰变值、提升值、变化趋势,排序,并绘图
    """)
    knowledge = ""
    for d in data:
        knowledge += d.get_text()

    # response: Union[str, List] = llm.call('你是关系型数据库 BI',' 根据数据库建表语句，生成数据库模型和领域模型图' + ddl.ddl_prompt, knowledge)
    # print(response)
    response: Union[str, List] = llm.call('你是关系型数据库 BI',' 根据数据库建表语句，生成 MySQL 8.0 直接运行的查询语句，sql语句中避免包含不明确的条件以及空 where 的情况' + ddl.ddl_prompt, knowledge)
    print(response)
    # 将文本写入 md 文件
    # 将 response 写入文件
    with open("output/response.md", "w", encoding="utf-8") as f:
        f.write(response)

    db_config = {
        'user': 'mayfair',
        'password': 'Mayfair@www4@',
        'host': 'shared-sg-testing.cluster-cdaqf1f1hpeh.ap-southeast-1.rds.amazonaws.com',
        'database': 'test_ai'
    }

    conn = mysql.connector.connect(**db_config)

    sqls = extractor.extract_sql_from_markdown(response)
    for sql in sqls:
        print(sql)
        extractor.execute_sql_and_save_to_csv(sql, conn, "output/output.csv" )

    conn.close()
