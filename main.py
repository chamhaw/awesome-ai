import os
from typing import List

import dashscope
from dotenv import load_dotenv
from llama_index.core.schema import NodeWithScore

from app.prompt import ddl

# 加载 .env 文件
load_dotenv()

from llama_index.core import QueryBundle

from app.llamaindex.file_parser import parse_directory
from app.llamaindex.indexer import initialize_index, add_documents, retrieve, get_query_engine



if __name__ == "__main__":
    data: List[NodeWithScore] = retrieve("test_index", """按照路线/路段/上下行/车道/路公司/管理中心/时间/数
    据来源/评价单元/指定起终点桩号,统计各项指标的均
    值、衰变值、提升值、变化趋势,排序,并绘图
    """)
    knowledge = ""
    for d in data:
        knowledge += d.get_text()
    print('knowledge:', knowledge)
    messages = [
        {'role': 'system', 'content': '你是关系型数据库 BI'},
        {'role': 'user', 'content': '背景知识:'+ knowledge + ' 根据数据库建表语句，生成SQL查询语句：' + ddl.ddl_prompt}
    ]
    response = dashscope.Generation.call(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        model="qwen-max", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=messages,
        result_format='text'
    )
    print(response.output.choices[0].message.content)
    # messages = [
    #     {'role': 'system', 'content': '你是关系型数据库 BI'},
    #     {'role': 'user', 'content': '提取出 SQL 语句:' + "基于你提供的数据库结构和需求，我们可以构建一个SQL查询语句来满足以下要求：按照路线/路段/上下行/车道/路公司/管理中心/时间/数据来源/评价单元/指定起终点桩号统计各项指标的均值、衰变值、提升值、变化趋势，并进行排序。此外，还需要对各路段的达标率、优等率等进行评定，并绘制车道级分级分色图。\n\n### SQL 查询生成\n\n假设用户想要查询某一路段（例如`G104`）在2023年的双侧PQI均值及其变化趋势，并且希望根据管养单位进行分组。以下是相应的SQL查询示例：\n\n```sql\nSELECT\n  `highway_code` AS '路线编码',\n  `highway_segment_simple_name` AS '路段简称',\n  `direction` AS '行车方向',\n  `roadway` AS '车道数',\n  `management_unit_name` AS '管养单位名称',\n  `check_year` AS '检测年份',\n  `data_source` AS '数据来源',\n  AVG(`bilateral_pqi`) AS '双侧PQI均值',\n  MAX(`bilateral_pqi`) - MIN(`bilateral_pqi`) AS '双侧PQI变化范围',\n  (MAX(`bilateral_pqi`) - MIN(`bilateral_pqi`)) / COUNT(*) AS '双侧PQI平均变化'\nFROM\n  `evaluation_0227_to_li`\nWHERE\n  `highway_code` = 'G104' AND\n  YEAR(`check_year`) = 2023 AND\n  `is_deleted` = 0\nGROUP BY\n  `highway_code`,\n  `highway_segment_simple_name`,\n  `direction`,\n  `roadway`,\n  `management_unit_name`,\n  `check_year`,\n  `data_source`\nORDER BY\n  `双侧PQI均值` DESC;\n```\n\n该查询将输出指定条件下的双侧PQI均值、最大最小值差（即变化范围），以及平均变化量，并按均值降序排列结果。\n\n### 达标率与优等率计算及绘图\n\n为了评估并可视化各路段的达标率与优等率，我们首先需要定义何为“达标”或“优等”。这通常依据行业标准如《公路技术状况评定标准 JTG5210-2018》来设定阈值。这里以双侧PQI为例，假定≥90为优等，≥85为达标，则可以进一步修改上述查询如下：\n\n```sql\nSELECT\n  ...\n  AVG(`bilateral_pqi`) AS '双侧PQI均值',\n  SUM(CASE WHEN `bilateral_pqi` >= 90 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS '双侧PQI优等率(%)',\n  SUM(CASE WHEN `bilateral_pqi` >= 85 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS '双侧PQI达标率(%)'\nFROM\n  ...\nGROUP BY\n  ...\nORDER BY\n  `双侧PQI均值` DESC;\n```\n\n此查询增加了两个字段：`双侧PQI优等率(%)` 和 `双侧PQI达标率(%)`，分别表示双侧PQI达到优等和达标水平的比例。\n\n### 可视化建议\n\n对于上述结果，可以使用Python中的matplotlib或者seaborn库进行可视化处理，比如创建柱状图展示不同管养单位之间的双侧PQI均值比较；利用折线图追踪特定路段随时间的变化趋势等。如果涉及到更复杂的地理信息可视化，则可能需要用到GeoPandas结合Folium或Plotly等工具来实现地图上的标记与着色。\n\n以上仅为基本框架，具体实现时还需考虑更多细节，包括但不限于异常值处理、性能优化等方面。"}
    # ]
    # response = dashscope.Generation.call(
    #     # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    #     api_key=os.getenv('DASHSCOPE_API_KEY'),
    #     model="qwen-max", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    #     messages=messages,
    #     result_format='message'
    # )
    # print(response.output.choices[0].message.content)

