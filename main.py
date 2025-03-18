
from dotenv import load_dotenv
# 加载 .env 文件
load_dotenv()

from typing import List, Union

from llama_index.core.schema import NodeWithScore

from app import llm
from app.prompt import ddl
from app.tool import extractor
from app.llamaindex.indexer import retrieve


if __name__ == "__main__":
    data: List[NodeWithScore] = retrieve("test_index", """按照路线/路段/上下行/车道/路公司/管理中心/时间/数
    据来源/评价单元/指定起终点桩号,统计各项指标的均
    值、衰变值、提升值、变化趋势,排序,并绘图
    """)
    knowledge = ""
    for d in data:
        knowledge += d.get_text()

    response: Union[str, List] = llm.call('你是关系型数据库 BI',' 根据数据库建表语句，生成SQL查询语句：' + ddl.ddl_prompt, knowledge)
    print(response)

    sqls = extractor.extract_sql_from_markdown(response)
    for sql in sqls:
        print(sql)


