"""
基于 Google ADK 的 BI 聊天代理
集成了SQL查询、数据分析和可视化建议功能
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Any
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from app.tool.sql import execute_sql_to_csv
from app.tool import extractor
from app.agent import store
from app.prompt.manager import prompt_manager
from app.prompt import system_prompts


class SQLExecutorTool:
    """SQL执行工具 - 简化的工具实现"""
    
    def __init__(self, db_config: Dict[str, Optional[str]]):
        self.db_config = db_config
        self.name = "sql_executor"
        self.description = "执行SQL查询并返回结果数据"
        
    def __call__(self, sql: str, session_id: str = "") -> Dict[str, Any]:
        """执行SQL查询"""
        try:
            if not session_id:
                session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
            
            csv_path = store.get_csv_path(session_id)
            # 确保db_config中的值不为None
            safe_db_config = {k: v for k, v in self.db_config.items() if v is not None}
            results = execute_sql_to_csv(sql, csv_path, safe_db_config)
            
            if results:
                return {
                    "success": True,
                    "content": results,
                    "csv_path": csv_path,
                    "sql": sql,
                    "row_count": len(results.split('\n')) - 1 if results else 0
                }
            else:
                return {
                    "success": False,
                    "content": "未查到任何统计数据，请重新调整查询条件",
                    "sql": sql
                }
                
        except Exception as e:
            return {
                "success": False,
                "content": f"SQL执行错误: {str(e)}",
                "sql": sql,
                "error": str(e)
            }


class ChartRecommendationTool:
    """图表推荐工具 - 简化的工具实现"""
    
    def __init__(self):
        self.name = "chart_recommender"
        self.description = "根据数据类型和查询内容推荐合适的图表类型"
        
    def __call__(self, query_content: str, data_sample: str = "") -> Dict[str, Any]:
        """推荐图表类型"""
        chart_types = {
            1: "柱状图 - 适合比较不同类别的数值",
            2: "折线图 - 适合显示趋势变化",
            3: "饼图 - 适合显示比例关系",
            4: "散点图 - 适合显示相关性",
            5: "条形图 - 适合显示排名",
            6: "面积图 - 适合显示累积数据",
            7: "热力图 - 适合显示矩阵数据"
        }
        
        # 简单的规则匹配来推荐图表类型
        query_lower = query_content.lower()
        
        if any(keyword in query_lower for keyword in ["趋势", "时间", "月份", "年份", "变化"]):
            chart_type = 2
        elif any(keyword in query_lower for keyword in ["比例", "占比", "百分比", "份额"]):
            chart_type = 3
        elif any(keyword in query_lower for keyword in ["排名", "排序", "前几", "前十"]):
            chart_type = 5
        elif any(keyword in query_lower for keyword in ["对比", "比较", "分类"]):
            chart_type = 1
        else:
            chart_type = 1  # 默认柱状图
            
        return {
            "success": True,
            "content": f"推荐使用图表编号: {chart_type}",
            "chart_type": chart_type,
            "chart_description": chart_types.get(chart_type, "柱状图"),
            "reason": f"基于查询内容'{query_content}'的分析"
        }


class BIChatAgent:
    """BI聊天代理"""
    
    def __init__(self):
        """初始化BI聊天代理"""
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME')
        }
        
        # 初始化工具
        self.sql_tool = SQLExecutorTool(self.db_config)
        self.chart_tool = ChartRecommendationTool()
        
        # 设置API密钥
        # api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        # if not api_key:
        #     raise ValueError("需要设置 GEMINI_API_KEY 环境变量")


        # 初始化 ADK 代理
        self.agent = LlmAgent(
            name="bi_chat_agent",
            model=LiteLlm(model="openai/gpt-4o"),
            description="专业的BI数据分析助手，能够理解自然语言查询并生成SQL语句执行数据查询",
            instruction=self._build_system_instruction(),
            tools=[self.sql_tool, self.chart_tool]
        )
        
    def _build_system_instruction(self) -> str:
        """构建系统指令"""
        ddl_sql = system_prompts.ddl_sql
        base_instruction = (
            "你是一个专业的BI数据分析助手。你的主要任务是：\n\n"
            "1. 理解用户的自然语言查询需求\n"
            "2. 分析查询意图，判断是否需要执行SQL查询\n"
            "3. 如果需要SQL查询，生成准确的MySQL 8.0查询语句\n"
            "4. 推荐合适的数据可视化图表类型\n"
            "5. 提供清晰、有洞察力的数据分析结果\n\n"
            f"数据库结构信息：\n{ddl_sql}\n\n"
            "工作流程：\n"
            "1. 首先分析用户查询，如果需要数据查询，在回复中包含 <analysis>需要SQL</analysis>\n"
            "2. 生成SQL语句并使用sql_executor工具执行\n"
            "3. 使用chart_recommender工具推荐合适的图表类型\n"
            "4. 分析查询结果并提供有价值的洞察\n\n"
            "注意事项：\n"
            "- 生成的SQL必须符合MySQL 8.0语法\n"
            "- 只查询确实存在的表和字段\n"
            "- 考虑数据的业务含义，提供有价值的分析\n"
            "- 推荐最适合数据展示的图表类型\n"
        )
        return base_instruction
    
    def process_query(self, user_query: str, session_id: Optional[str] = None) -> Tuple[str, str, str, int, str]:
        """
        处理用户查询
        
        Returns:
            Tuple[response, sql, csv_results, chart_type, csv_path]
        """
        if not session_id:
            session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
            
        try:
            # 简化的处理逻辑 - 直接使用现有的流程
            response = f"基于ADK处理查询: {user_query}"
            
            # 检查是否需要SQL查询
            if "<analysis>需要SQL</analysis>" not in response:
                # 这里可以增加LLM调用来判断是否需要SQL
                needs_sql = any(keyword in user_query.lower() for keyword in ["查询", "统计", "数据", "多少", "列表"])
                if needs_sql:
                    response += "\n<analysis>需要SQL</analysis>"
            
            if "<analysis>需要SQL</analysis>" not in response:
                return response, "", "", 1, ""
            
            # 提取SQL语句 - 这里简化处理
            sqls = extractor.extract_sql_queries(response)
            if not sqls:
                # 生成一个简单的测试SQL
                sqls = ["SELECT 1 as test_result"]
                
            sql = sqls[0]  # 使用第一个SQL语句
            csv_results = ""
            chart_type = 1
            csv_path = ""
            
            # 执行SQL
            sql_result = self.sql_tool(sql, session_id)
            if sql_result.get("success"):
                csv_results = sql_result.get("content", "")
                csv_path = sql_result.get("csv_path", "")
                
                # 推荐图表类型
                chart_result = self.chart_tool(user_query, csv_results)
                if chart_result.get("success"):
                    chart_type = chart_result.get("chart_type", 1)
            else:
                response = sql_result.get("content", "查询失败")
            
            return response, sql, csv_results, chart_type, csv_path
            
        except Exception as e:
            error_response = f"处理查询时发生错误: {str(e)}"
            return error_response, "", "", 1, ""
    
    def get_analysis_suggestion(self, query: str, data_result: str) -> str:
        """获取数据分析建议"""
        try:
            analysis_prompt = f"""
基于以下查询和数据结果，请提供专业的数据分析洞察：

查询问题: {query}
数据结果: {data_result}

请分析：
1. 数据的主要趋势和模式
2. 关键发现和异常点
3. 业务意义和建议
4. 可能的后续分析方向
            """
            
            # 这里可以调用LLM API来生成分析建议
            return f"基于查询'{query}'的分析建议: 数据显示了相关的业务趋势，建议进一步分析..."
            
        except Exception as e:
            return f"分析建议生成失败: {str(e)}"
    
    def validate_sql(self, sql: str) -> bool:
        """验证SQL语句的合法性"""
        try:
            # 基本的SQL验证
            sql_lower = sql.lower().strip()
            
            # 检查是否是查询语句
            if not sql_lower.startswith('select'):
                return False
                
            # 检查是否包含危险操作
            dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'create', 'alter']
            if any(keyword in sql_lower for keyword in dangerous_keywords):
                return False
                
            return True
            
        except Exception:
            return False


def create_bi_agent(gemini_api_key: Optional[str] = None) -> BIChatAgent:
    """创建BI聊天代理实例"""
    return BIChatAgent()