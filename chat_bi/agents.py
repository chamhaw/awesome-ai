"""
ADK Agents 模块
基于Google ADK 1.1.1实现的智能代理
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from app.prompt.manager import prompt_manager
from .tools import SQLExecutor, ChartRecommender, DataValidator, QueryExtractor
from .config import app_config
from chat_bi import store
from chat_bi.knowledge import get_knowledge


class BIAgent:
    """核心BI数据分析代理"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化BI代理
        
        Args:
            gemini_api_key: Gemini API密钥，如果为None则从配置中获取
        """
        # # 设置API密钥
        # api_key = api_key or app_config.llm.gemini_api_key
        # if not api_key:
        #     raise ValueError("需要设置 GEMINI_API_KEY 环境变量或传入api_key参数")
        
        # 配置环境变量
        for key, value in app_config.get_active_llm_config().items():
            os.environ[key] = value
        
        # 初始化工具
        self.sql_executor = SQLExecutor()
        self.chart_recommender = ChartRecommender()
        self.data_validator = DataValidator()
        self.query_extractor = QueryExtractor()
        
        # 初始化SQL代理
        self.sql_agent = SQLAgent()
        
        # 初始化ADK代理
        self.agent = LlmAgent(
            name="bi_agent",
            model = LiteLlm(model=f'{app_config.llm.default_provider}/{app_config.llm.default_model}'),
            description="专业的BI数据分析助手，能够理解自然语言查询并生成SQL语句执行数据查询",
            instruction=self._build_system_instruction(),
            tools=[self.sql_executor, self.chart_recommender, self.data_validator]
            )
        
        # 初始化Session服务和Runner
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="bi_app",
            session_service=self.session_service
        )
        
    def _build_system_instruction(self) -> str:
        """构建系统指令"""
        # 获取知识库内容
        knowledge = get_knowledge("BI数据分析")
        if len(knowledge) > 100000:
            knowledge = knowledge[-100000:]
        
        base_instruction = f"""
你是一个专业的BI数据分析助手，基于Google ADK构建。你的主要任务是：

1. 理解用户的自然语言查询需求
2. 分析查询意图，判断是否需要执行SQL查询
3. 如果需要SQL查询，生成准确的MySQL 8.0查询语句
4. 推荐合适的数据可视化图表类型
5. 验证数据质量并提供改进建议
6. 提供清晰、有洞察力的数据分析结果

知识库信息：
<context>
{knowledge}
</context>

 数据库结构信息：
 {prompt_manager.load("ddl_sql")}

工作流程：
1. 首先分析用户查询，如果需要数据查询，在回复中包含 <analysis>需要SQL</analysis>
2. 生成SQL语句并使用sql_executor工具执行
3. 使用data_validator工具验证数据质量
4. 使用chart_recommender工具推荐合适的图表类型
5. 分析查询结果并提供有价值的洞察

注意事项：
- 生成的SQL必须符合MySQL 8.0语法
- 只查询确实存在的表和字段
- 考虑数据的业务含义，提供有价值的分析
- 推荐最适合数据展示的图表类型
- 关注数据质量问题并提供改进建议
        """
        
        return base_instruction.strip()
    
    def process_query(self, user_query: str, session_id: Optional[str] = None) -> Tuple[str, str, str, int, str]:
        """
        处理用户查询，支持多轮对话
        
        Args:
            user_query: 用户查询内容
            session_id: 会话ID
            
        Returns:
            Tuple[response, sql, csv_results, chart_type, csv_path]
        """
        if not session_id:
            session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
            
        try:
            # 获取历史对话记录
            history = store.get_session_history(session_id)
            
            # 准备系统提示词和历史记录（使用 store 模块）
            system_prompt, updated_history = store.prompt_prepare(
                user_query, 
                "", 
                session_id, 
                history
            )
            
            # 分析查询意图
            intent_info = self.query_extractor.extract_analysis_intent(user_query)
            
            # 构建增强的查询上下文，包含历史记录
            context_parts = []
            if updated_history:
                context_parts.append("历史对话记录:")
                for msg in updated_history[-3:]:  # 只保留最近3条记录作为上下文
                    role = "用户" if msg.role == "user" else "助手"
                    context_parts.append(f"{role}: {msg.content}")
                context_parts.append("")
            
            context_parts.extend([
                f"当前用户查询: {user_query}",
                f"分析意图: {intent_info.get('primary_intent', 'general')}",
                f"置信度: {intent_info.get('confidence', 0):.2f}",
                "",
                "请分析此查询并决定是否需要执行SQL查询。如果需要，请在回复中包含 <analysis>需要SQL</analysis>"
            ])
            
            enhanced_query = "\n".join(context_parts)
            
            # 创建会话（如果不存在）- 使用同步方式
            try:
                import asyncio
                
                async def create_session_async():
                    return await self.session_service.create_session(
                        app_name="bi_app",
                        user_id="default_user",
                        session_id=session_id
                    )
                
                # 尝试在当前事件循环中创建会话
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 如果已有事件循环在运行，跳过会话创建
                        pass
                    else:
                        loop.run_until_complete(create_session_async())
                except RuntimeError:
                    # 事件循环问题，跳过会话创建
                    pass
            except Exception:
                # 会话可能已存在，忽略错误
                pass
            
            # 基于历史记录和当前查询生成响应
            response = f"基于ADK处理查询: {user_query}\n分析意图: {intent_info['primary_intent']}"
            
            # 检查是否需要SQL查询
            needs_sql = self._should_execute_sql(user_query, intent_info)
            if needs_sql:
                response += "\n<analysis>需要SQL</analysis>"
            
            # 创建新的消息对象并更新历史记录
            from dashscope.api_entities.dashscope_response import Message
            
            # 添加用户消息到历史记录
            user_message = Message(role="user", content=user_query)
            updated_history.append(user_message)
            
            if "<analysis>需要SQL</analysis>" not in response:
                # 不需要SQL查询，直接返回回答
                assistant_message = Message(role="assistant", content=response)
                updated_history.append(assistant_message)
                
                # 存储更新后的历史记录
                store.store_context(session_id, updated_history)
                
                return response, "", "", 1, ""
            
            # 提取或生成SQL语句
            sql_queries = self.query_extractor.extract_sql_queries(response)
            if not sql_queries:
                # 使用SQLAgent生成SQL
                sql_result = self.sql_agent.generate_sql(user_query)
                if sql_result.get("success"):
                    sql_queries = [sql_result.get("sql")]
                elif sql_result.get("message"):
                    message = sql_result.get("message") or "SQL生成失败"
                    return message, "", "", 1, ""
                else:
                    # 如果SQL生成失败，返回错误信息
                    error_msg = f"SQL生成失败: {sql_result.get('error', '未知错误')}"
                    assistant_message = Message(role="assistant", content=error_msg)
                    updated_history.append(assistant_message)
                    store.store_context(session_id, updated_history)
                    return error_msg, "", "", 1, ""
            
            sql = sql_queries[0] if sql_queries and sql_queries[0] else ""
            if not sql:
                error_msg = "未能生成有效的SQL查询"
                assistant_message = Message(role="assistant", content=error_msg)
                updated_history.append(assistant_message)
                store.store_context(session_id, updated_history)
                return error_msg, "", "", 1, ""
            
            csv_results = ""
            chart_type = 1
            csv_path = ""
            
            # 执行SQL
            sql_result = self.sql_executor(sql, session_id)
            if sql_result.get("success"):
                csv_results = sql_result.get("content", "")
                csv_path = sql_result.get("csv_path", "")
                
                # 验证数据质量
                validation_result = self.data_validator(csv_results)
                if validation_result.get("success") and validation_result.get("recommendations"):
                    response += f"\n数据质量建议: {'; '.join(validation_result['recommendations'])}"
                
                # 推荐图表类型
                chart_result = self.chart_recommender(user_query, csv_results)
                if chart_result.get("success"):
                    chart_type = chart_result.get("chart_type", 1)
                    response += f"\n图表推荐: {chart_result.get('chart_description', '')}"
                
                # 构建完整的响应信息
                full_response = f"{response}\n\nSQL查询: {sql}\n查询结果已生成"
            else:
                full_response = sql_result.get("content", "查询失败")
            
            # 添加助手回复到历史记录
            assistant_message = Message(role="assistant", content=full_response)
            updated_history.append(assistant_message)
            
            # 存储更新后的历史记录
            store.store_context(session_id, updated_history)
            
            return response, sql, csv_results, chart_type, csv_path
            
        except Exception as e:
            error_response = f"处理查询时发生错误: {str(e)}"
            
            # 即使出错也要尝试记录历史
            try:
                from dashscope.api_entities.dashscope_response import Message
                history = store.get_session_history(session_id)
                user_message = Message(role="user", content=user_query)
                error_message = Message(role="assistant", content=error_response)
                history.extend([user_message, error_message])
                store.store_context(session_id, history)
            except:
                pass  # 忽略历史记录保存错误
                
            return error_response, "", "", 1, ""
    
    def _should_execute_sql(self, user_query: str, intent_info: Dict[str, Any]) -> bool:
        """判断是否需要执行SQL查询"""
        # 基于关键词和意图判断
        sql_keywords = ["查询", "统计", "数据", "多少", "列表", "显示", "分析", "报告"]
        query_lower = user_query.lower()
        
        # 如果包含SQL关键词或者意图不是一般性查询
        return any(keyword in query_lower for keyword in sql_keywords) or intent_info.get('primary_intent') != 'general'
    
    async def process_query_async(self, user_query: str, session_id: Optional[str] = None) -> Tuple[str, str, str, int, str]:
        """
        异步处理用户查询，实际调用ADK大模型
        
        Args:
            user_query: 用户查询内容
            session_id: 会话ID
            
        Returns:
            Tuple[response, sql, csv_results, chart_type, csv_path]
        """
        if not session_id:
            session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
            
        try:
            # 分析查询意图
            intent_info = self.query_extractor.extract_analysis_intent(user_query)
            
            # 构建增强的查询上下文
            enhanced_query = f"""
用户查询: {user_query}
分析意图: {intent_info.get('primary_intent', 'general')}
置信度: {intent_info.get('confidence', 0):.2f}

请分析此查询并决定是否需要执行SQL查询。如果需要，请在回复中包含 <analysis>需要SQL</analysis>
            """
            
            # 创建会话（如果不存在）
            try:
                await self.session_service.create_session(
                    app_name="bi_app",
                    user_id="default_user",
                    session_id=session_id
                )
            except Exception:
                # 会话可能已存在，忽略错误
                pass
            
            # 使用ADK Runner处理查询
            user_content = types.Content(
                role='user',
                parts=[types.Part(text=enhanced_query)]
            )
            
            final_response = ""
            
            # 处理ADK响应
            async for event in self.runner.run_async(
                user_id="default_user",
                session_id=session_id,
                new_message=user_content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                    break
            
            response = final_response or f"基于ADK处理查询: {user_query}"
            
            # 检查是否需要SQL查询
            if "<analysis>需要SQL</analysis>" not in response:
                return response, "", "", 1, ""
            
            # 提取或生成SQL语句
            sql_queries = self.query_extractor.extract_sql_queries(response)
            if not sql_queries:
                # 使用SQLAgent生成SQL
                sql_result = self.sql_agent.generate_sql(user_query)
                if sql_result.get("success"):
                    sql_queries = [sql_result.get("sql")]
                elif sql_result.get("message"):
                    message = sql_result.get("message") or "SQL生成失败"
                    return message, "", "", 1, ""
                else:
                    # 如果SQL生成失败，返回错误信息
                    error_msg = f"SQL生成失败: {sql_result.get('error', '未知错误')}"
                    return error_msg, "", "", 1, ""
            
            sql = sql_queries[0] if sql_queries and sql_queries[0] else ""
            if not sql:
                return "未能生成有效的SQL查询", "", "", 1, ""
            
            csv_results = ""
            chart_type = 1
            csv_path = ""
            
            # 执行SQL
            sql_result = self.sql_executor(sql, session_id)
            if sql_result.get("success"):
                csv_results = sql_result.get("content", "")
                csv_path = sql_result.get("csv_path", "")
                
                # 验证数据质量
                validation_result = self.data_validator(csv_results)
                if validation_result.get("success") and validation_result.get("recommendations"):
                    response += f"\n数据质量建议: {'; '.join(validation_result['recommendations'])}"
                
                # 推荐图表类型
                chart_result = self.chart_recommender(user_query, csv_results)
                if chart_result.get("success"):
                    chart_type = chart_result.get("chart_type", 1)
                    response += f"\n图表推荐: {chart_result.get('chart_description', '')}"
            else:
                response = sql_result.get("content", "查询失败")
            
            return response, sql, csv_results, chart_type, csv_path
            
        except Exception as e:
            error_response = f"处理查询时发生错误: {str(e)}"
            return error_response, "", "", 1, ""
    
    def get_analysis_suggestion(self, query: str, data_result: str) -> str:
        """获取数据分析建议"""
        try:
            # 如果没有初始化分析代理，则创建一个
            if not hasattr(self, 'analysis_agent'):
                self.analysis_agent = AnalysisAgent()
            
            # 使用AnalysisAgent进行分析
            analysis_result = self.analysis_agent.analyze_data(data_result, query)
            
            if analysis_result.get("success"):
                analysis_report = analysis_result.get("analysis", {})
                
                # 构建分析建议文本
                suggestions = []
                
                # 添加洞察
                insights = analysis_report.get("insights", [])
                if insights:
                    suggestions.append("数据洞察:")
                    suggestions.extend([f"- {insight}" for insight in insights])
                
                # 添加建议
                recommendations = analysis_report.get("recommendations", [])
                if recommendations:
                    suggestions.append("\n改进建议:")
                    suggestions.extend([f"- {rec}" for rec in recommendations])
                
                # 添加图表建议
                chart_info = analysis_report.get("chart_recommendation", {})
                if chart_info.get("success"):
                    chart_desc = chart_info.get("chart_description", "")
                    if chart_desc:
                        suggestions.append(f"\n可视化建议: {chart_desc}")
                
                return "\n".join(suggestions) if suggestions else f"基于查询'{query}'完成了数据分析"
            else:
                return f"分析失败: {analysis_result.get('error', '未知错误')}"
            
        except Exception as e:
            return f"分析建议生成失败: {str(e)}"

    def clear_session(self, session_id: str):
        """清除指定会话的历史记录"""
        store.clear_session(session_id)
    
    def get_session_history(self, session_id: str):
        """获取指定会话的历史记录"""
        return store.get_session_history(session_id)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话摘要信息"""
        history = store.get_session_history(session_id)
        return {
            "session_id": session_id,
            "message_count": len(history),
            "last_activity": max([msg.get('timestamp', '') for msg in history]) if history else "",
            "conversation_length": sum(len(msg.content) for msg in history),
            "has_sql_queries": any("<analysis>需要SQL</analysis>" in msg.content for msg in history if msg.role == "assistant")
        }


class SQLAgent:
    """专门的SQL生成和执行代理"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """初始化SQL代理"""
        # api_key = gemini_api_key or app_config.llm.gemini_api_key
        # if not api_key:
        #     raise ValueError("需要设置 GEMINI_API_KEY 环境变量")
        
        # 配置环境变量
        for key, value in app_config.get_active_llm_config().items():
            os.environ[key] = value
        
        self.sql_executor = SQLExecutor()
        self.query_extractor = QueryExtractor()
        
        # 专门用于SQL生成的ADK代理
        self.agent = LlmAgent(
            name="sql_agent",
            model=LiteLlm(model=f'{app_config.llm.default_provider}/{app_config.llm.default_model}'),
            description="专门负责SQL查询生成和执行的代理",
            instruction=self._build_sql_instruction(),
            tools=[self.sql_executor]
        )
        
        # 初始化Session服务和Runner
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="sql_app",
            session_service=self.session_service
        )
    
    def _build_sql_instruction(self) -> str:
        """构建SQL专用指令"""
        # 获取知识库内容并格式化模板
        knowledge = get_knowledge("SQL查询生成")
        if len(knowledge) > 100000:
            knowledge = knowledge[-100000:]
        
        try:
            return prompt_manager.render("gen_sql", knowledge=knowledge)
        except Exception as e:
            print(f"⚠️ 格式化SQL指令时出错: {e}")
            # 如果格式化失败，使用备用指令
            return f"""
你是一个专业的SQL查询专家。你的任务是：

1. 理解用户的数据查询需求
2. 生成准确、高效的MySQL 8.0查询语句
3. 确保查询的安全性和性能

知识库信息：
<context>
{knowledge}
</context>

数据库结构：
{prompt_manager.load("ddl_sql")}

规则：
- 只生成SELECT查询语句
- 使用适当的索引和条件优化性能
- 避免复杂的嵌套查询，优先使用JOIN
- 对于大数据量查询添加LIMIT限制
            """
    
    def generate_sql(self, user_query: str) -> Dict[str, Any]:
        """生成SQL查询"""
        try:
            # 首先尝试从查询中提取现有的SQL
            extracted_queries = self.query_extractor.extract_sql_queries(user_query)
            
            if extracted_queries:
                sql = extracted_queries[0]
            else:
                # 使用大模型生成SQL
                sql = self._generate_sql_from_query(user_query)
                sqls = self.query_extractor.extract_sql_queries(sql)
                if sqls:
                    sql = sqls[0]
                else:
                    # 如果仍然无效，尝试添加提示
                    if  "</hint>" in sql:
                    # 如果仍然无效,返回错误
                        return {
                            "success": False,
                            "message": sql
                        }
            return {
                "success": True,
                "sql": sql,
                "explanation": f"为查询'{user_query}'生成的SQL语句"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_sql_from_query(self, query: str) -> str:
        """基于查询内容生成SQL"""
        try:
            # 构建SQL生成提示
#             sql_prompt = f"""
# 基于用户查询生成MySQL 8.0 SQL语句：
#
# 用户查询: {query}
#
# 数据库结构：
# {prompt_manager.load("ddl_sql")}
#
# 要求：
# 1. 只生成SELECT查询语句
# 2. 确保查询语法正确
# 3. 添加适当的LIMIT限制
# 4. 使用合适的JOIN和WHERE条件
# 5. 返回纯SQL语句，不要其他说明
#
# SQL语句：
#             """
            
            # 使用ADK代理的模型直接生成SQL
            from google.genai import types
            
            # 创建临时会话进行SQL生成
            user_content = types.Content(
                role='user',
                parts=[types.Part(text=query)]
            )
            
            # 同步调用模型生成SQL
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 在已有事件循环中，抛出错误而不是使用备用逻辑
                    raise RuntimeError("当前在事件循环中运行，无法同步生成SQL，请使用异步方法")
                else:
                    # 创建新的事件循环
                    async def generate_sql_async():
                        session_id = f"sql_gen_{int(time.time())}"
                        try:
                            await self.session_service.create_session(
                                app_name="sql_app",
                                user_id="sql_user", 
                                session_id=session_id
                            )
                        except:
                            pass
                        
                        async for event in self.runner.run_async(
                            user_id="sql_user",
                            session_id=session_id,
                            new_message=user_content
                        ):
                            if event.is_final_response() and event.content and event.content.parts:
                                sql_text = event.content.parts[0].text
                                if sql_text:
                                    sql_text = sql_text.strip()
                                    # 提取SQL语句
                                    if "SELECT" in sql_text.upper():
                                        lines = sql_text.split('\n')
                                        for line in lines:
                                            if line.strip().upper().startswith('SELECT'):
                                                return line.strip()
                                    return sql_text
                        # 如果没有生成有效SQL，抛出错误
                        raise ValueError(f"无法为查询 '{query}' 生成有效的SQL语句")
                    
                    return loop.run_until_complete(generate_sql_async())
            except Exception as e:
                # 不再使用备用逻辑，直接重新抛出异常
                raise RuntimeError(f"SQL生成失败: {str(e)}") from e
                
        except Exception as e:
            # 不再使用备用逻辑，直接重新抛出异常
            raise RuntimeError(f"SQL生成过程中发生错误: {str(e)}") from e


class AnalysisAgent:
    """专门的数据分析代理"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """初始化分析代理"""
        # api_key = gemini_api_key or app_config.llm.gemini_api_key
        # if not api_key:
        #     raise ValueError("需要设置 GEMINI_API_KEY 环境变量")
        
        # 配置环境变量
        for key, value in app_config.get_active_llm_config().items():
            os.environ[key] = value
        
        self.chart_recommender = ChartRecommender()
        self.data_validator = DataValidator()
        
        # 专门用于数据分析的ADK代理
        self.agent = LlmAgent(
            name="analysis_agent",
            model=LiteLlm(model=f'{app_config.llm.default_provider}/{app_config.llm.default_model}'),
            description="专门负责数据分析和可视化建议的代理",
            instruction=self._build_analysis_instruction(),
            tools=[self.chart_recommender, self.data_validator]
        )
        
        # 初始化Session服务和Runner
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="analysis_app",
            session_service=self.session_service
        )
    
    def _build_analysis_instruction(self) -> str:
        """构建分析专用指令"""
        return """
你是一个专业的数据分析师。你的任务是：

1. 分析数据的统计特征和分布
2. 识别数据中的趋势、模式和异常
3. 推荐合适的可视化图表类型
4. 提供有价值的业务洞察和建议

分析重点：
- 数据质量评估
- 统计描述分析
- 趋势和相关性分析
- 业务价值挖掘
        """
    
    def analyze_data(self, data: str, query_context: str = "") -> Dict[str, Any]:
        """分析数据并提供洞察"""
        try:
            # 验证数据质量
            validation_result = self.data_validator(data)
            
            # 推荐图表类型
            chart_result = self.chart_recommender(query_context, data)
            
            # 生成分析报告
            analysis_report = {
                "data_quality": validation_result,
                "chart_recommendation": chart_result,
                "insights": self._generate_insights(data, validation_result),
                "recommendations": self._generate_recommendations(data, query_context)
            }
            
            return {
                "success": True,
                "analysis": analysis_report
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_insights(self, data: str, quality_info: Dict[str, Any]) -> List[str]:
        """生成数据洞察"""
        insights = []
        
        try:
            # 构建洞察生成提示
            insight_prompt = f"""
基于以下数据分析结果，请提供专业的数据洞察：

数据内容: {data[:1000]}...  # 限制长度避免过长
数据质量信息: {quality_info}

请分析并提供洞察：
1. 数据的主要特征和分布模式
2. 关键趋势和异常发现
3. 数据中的重要关联和相关性
4. 可能的业务含义和价值

请以简洁的要点形式返回洞察，每个洞察一行：
            """
            
            # 使用模型生成洞察
            from google.genai import types
            user_content = types.Content(
                role='user', 
                parts=[types.Part(text=insight_prompt)]
            )
            
            # 尝试异步生成洞察
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    async def generate_insights_async():
                        session_id = f"insight_{int(time.time())}"
                        try:
                            await self.session_service.create_session(
                                app_name="analysis_app",
                                user_id="analysis_user",
                                session_id=session_id
                            )
                        except:
                            pass
                        
                        async for event in self.runner.run_async(
                            user_id="analysis_user",
                            session_id=session_id,
                            new_message=user_content
                        ):
                            if event.is_final_response() and event.content and event.content.parts:
                                insight_text = event.content.parts[0].text
                                if insight_text:
                                    # 解析洞察文本为列表
                                    insight_lines = [line.strip() for line in insight_text.split('\n') if line.strip()]
                                    return insight_lines[:5]  # 限制返回数量
                        # 如果没有生成洞察，抛出错误
                        raise ValueError(f"无法生成数据洞察")
                    
                    insights = loop.run_until_complete(generate_insights_async())
                else:
                    # 在事件循环中运行，抛出错误
                    raise RuntimeError("当前在事件循环中运行，无法同步生成洞察")
            except Exception as e:
                # 不再使用备用逻辑，直接抛出异常
                raise RuntimeError(f"洞察生成失败: {str(e)}") from e
                
        except Exception as e:
            # 不再使用备用逻辑，直接抛出异常
            raise RuntimeError(f"洞察生成过程中发生错误: {str(e)}") from e
        
        return insights
    
    def _generate_recommendations(self, data: str, query_context: str) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        try:
            # 构建建议生成提示
            recommendation_prompt = f"""
基于以下数据分析结果和查询上下文，请提供专业的业务建议：

查询上下文: {query_context}
数据内容: {data[:1000]}...  # 限制长度

请提供针对性的建议：
1. 数据质量改进建议
2. 进一步分析方向
3. 业务决策支持建议
4. 数据收集和处理优化建议

请以简洁的要点形式返回建议，每个建议一行：
            """
            
            # 使用模型生成建议
            from google.genai import types
            user_content = types.Content(
                role='user',
                parts=[types.Part(text=recommendation_prompt)]
            )
            
            # 尝试异步生成建议
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    async def generate_recommendations_async():
                        session_id = f"rec_{int(time.time())}"
                        try:
                            await self.session_service.create_session(
                                app_name="analysis_app",
                                user_id="analysis_user",
                                session_id=session_id
                            )
                        except:
                            pass
                        
                        async for event in self.runner.run_async(
                            user_id="analysis_user",
                            session_id=session_id,
                            new_message=user_content
                        ):
                            if event.is_final_response() and event.content and event.content.parts:
                                rec_text = event.content.parts[0].text
                                if rec_text:
                                    # 解析建议文本为列表
                                    rec_lines = [line.strip() for line in rec_text.split('\n') if line.strip()]
                                    return rec_lines[:5]  # 限制返回数量
                        # 如果没有生成建议，抛出错误
                        raise ValueError(f"无法生成改进建议")
                    
                    recommendations = loop.run_until_complete(generate_recommendations_async())
                else:
                    # 在事件循环中运行，抛出错误
                    raise RuntimeError("当前在事件循环中运行，无法同步生成建议")
            except Exception as e:
                # 不再使用备用逻辑，直接抛出异常
                raise RuntimeError(f"建议生成失败: {str(e)}") from e
                
        except Exception as e:
            # 不再使用备用逻辑，直接抛出异常
            raise RuntimeError(f"建议生成过程中发生错误: {str(e)}") from e
        
        return recommendations 