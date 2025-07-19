"""
ADK Server 模块
基于Flask的ADK应用服务器，保持原有API兼容性
"""

import os
import re
import time
from urllib.parse import quote
from typing import Optional

from flask import Flask, request, jsonify, make_response, send_file
from flasgger import Swagger, swag_from
from bs4 import BeautifulSoup

# 导入原有模块以保持兼容性
from app.prompt import system_prompts
from chat_bi import store
from app.cli import CLIChat
from app.tool.sql import execute_sql_to_csv

# 导入新的ADK模块
from .agents import BIAgent, SQLAgent, AnalysisAgent
from .config import app_config


def create_app() -> Flask:
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置Swagger
    swagger = Swagger(app)
    app.config['SWAGGER'] = {
        "title": "Awesome AI 接口文档",
        "version": "2.0",
        "description": "API Documentation - 基于Google ADK 1.1.1的智能BI聊天助手",
        "specs_route": "/apidocs/",
        "headers": [],
    }
    
    # 初始化原有的CLI聊天（保持兼容性）
    legacy_chat = CLIChat()
    
    # 初始化ADK代理
    adk_agents = _initialize_adk_agents()
    
    # 注册路由
    _register_routes(app, adk_agents)
    
    return app


def _initialize_adk_agents() -> dict:
    """初始化ADK代理"""
    agents = {}
    
    try:
        # 初始化主BI代理
        agents['bi_agent'] = BIAgent()
        print("✅ ADK BI Agent 初始化成功")
    except Exception as e:
        agents['bi_agent'] = None
        print(f"⚠️ ADK BI Agent 初始化失败: {e}")
    
    try:
        # 初始化SQL代理
        agents['sql_agent'] = SQLAgent()
        print("✅ ADK SQL Agent 初始化成功")
    except Exception as e:
        agents['sql_agent'] = None
        print(f"⚠️ ADK SQL Agent 初始化失败: {e}")
    
    try:
        # 初始化分析代理
        agents['analysis_agent'] = AnalysisAgent()
        print("✅ ADK Analysis Agent 初始化成功")
    except Exception as e:
        agents['analysis_agent'] = None
        print(f"⚠️ ADK Analysis Agent 初始化失败: {e}")
    
    return agents


def _register_routes(app: Flask, adk_agents: dict):
    """注册所有路由 - 完全基于ADK agents实现"""
    
    # 主要聊天API端点 - 改为使用ADK agents
    @app.route('/api/chat', methods=['POST'])
    @swag_from('../doc/chat.yaml')
    def generate_sql():
        """生成SQL语句 - ADK实现"""
        data = request.get_json() or {}
        raw_user_prompt = data.get('user_prompt', '')
        
        if not raw_user_prompt:
            return jsonify({"error": "user_prompt 参数不能为空"}), 400
        
        # 从cookie或生成新的session_id
        session_id = request.cookies.get('x-session-id')
        clear = data.get('clear', False)
        
        if clear or not session_id:
            session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        
        # 获取BI代理
        bi_agent: BIAgent | None = adk_agents.get('bi_agent')
        if not bi_agent:
            return jsonify({
                "error": "ADK BI Agent未初始化",
                "message": "请检查GEMINI_API_KEY环境变量是否设置正确"
            }), 500
        
        try:
            # 使用ADK BI Agent处理查询
            response, sql, csv_results, chart_type, csv_path = bi_agent.process_query(
                raw_user_prompt, session_id
            )
            
            response_body = {}
            
            # 如果不需要SQL查询，直接返回回答
            if "<analysis>需要SQL</analysis>" not in response:
                response_body['message'] = response
                resp = make_response(response_body)
                resp.set_cookie('x-session-id', session_id,
                                httponly=True, secure=True, max_age=1800)
                return resp
            
            # 需要SQL查询的情况
            response_body['sql'] = sql
            if not csv_results:
                response_body['message'] = "未查到任何统计数据，请重新调整查询条件"
            else:
                response_body['chart_type'] = chart_type
                response_body['csv'] = csv_results
                response_body['file_path'] = csv_path
                response_body['file_link'] = f"{app_config.server.server_url}/api/download_file?file_path={quote(csv_path)}"
            
            resp = make_response(response_body)
            resp.set_cookie('x-session-id', session_id,
                            httponly=True, secure=True, max_age=1800)
            return resp
            
        except Exception as e:
            import traceback
            import logging
            
            # 配置日志记录
            logging.basicConfig(level=logging.ERROR)
            logger = logging.getLogger(__name__)
            
            # 记录完整的错误堆栈信息
            error_traceback = traceback.format_exc()
            logger.error(f"API /api/chat 处理失败:\n{error_traceback}")
            
            # 也打印到控制台，方便调试
            print(f"❌ /api/chat 接口异常:")
            print(f"错误信息: {str(e)}")
            print(f"完整堆栈:\n{error_traceback}")
            
            return jsonify({
                "error": f"处理查询时发生错误: {str(e)}",
                "message": "SQL生成失败: SQL生成过程中发生错误: SQL生成失败: 'Context variable not found: `knowledge`.'",
                "debug_info": {
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "traceback": error_traceback
                }
            }), 500

    # ADK增强API端点 - 保持不变
    @app.route('/api/adk-chat', methods=['POST'])
    def adk_chat():
        """基于Google ADK的BI聊天接口
        ---
        tags:
          - ADK Chat
        summary: ADK BI聊天助手
        description: 使用Google ADK 1.1.1构建的智能BI数据分析助手
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                user_prompt:
                  type: string
                  description: 用户查询
                  example: "查询销售数据趋势"
                session_id:
                  type: string
                  description: 会话ID (可选)
                clear:
                  type: boolean
                  description: 是否清除历史
                  default: false
                agent_type:
                  type: string
                  description: 代理类型 (bi, sql, analysis)
                  default: "bi"
                  enum: ["bi", "sql", "analysis"]
        responses:
          200:
            description: 成功返回响应
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: AI回复消息
                sql:
                  type: string
                  description: 生成的SQL语句
                csv:
                  type: string
                  description: 查询结果数据
                chart_type:
                  type: integer
                  description: 推荐的图表类型
                file_path:
                  type: string
                  description: CSV文件路径
                file_link:
                  type: string
                  description: CSV下载链接
                adk_powered:
                  type: boolean
                  description: 是否由ADK提供支持
                agent_info:
                  type: object
                  description: 使用的代理信息
          500:
            description: 内部服务器错误
        """
        data = request.get_json() or {}
        raw_user_prompt = data.get('user_prompt', '')
        session_id = data.get('session_id') or request.cookies.get('x-session-id')
        clear = data.get('clear', False)
        agent_type = data.get('agent_type', 'bi')
        
        if clear:
            session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        
        if not session_id:
            session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        
        # 选择合适的代理
        agent = adk_agents.get(f'{agent_type}_agent')
        if not agent:
            return jsonify({
                "error": f"ADK {agent_type.upper()} Agent未能成功初始化",
                "message": "请检查GEMINI_API_KEY环境变量是否设置正确",
                "adk_powered": True
            }), 500
        
        try:
            if agent_type == 'bi':
                # 使用BI代理处理查询
                response, sql, csv_results, chart_type, csv_path = agent.process_query(
                    raw_user_prompt, session_id
                )
                
                response_body = {
                    "adk_powered": True,
                    "agent_info": {"type": "bi", "model": app_config.llm.default_model},
                    "message": response
                }
                
                if sql:
                    response_body['sql'] = sql
                    
                if csv_results:
                    response_body['csv'] = csv_results
                    response_body['chart_type'] = chart_type
                    response_body['file_path'] = csv_path
                    response_body['file_link'] = f"{app_config.server.server_url}/api/download_file?file_path={quote(csv_path)}"
                    
            elif agent_type == 'sql':
                # 使用SQL代理生成SQL
                sql_result = agent.generate_sql(raw_user_prompt)
                response_body = {
                    "adk_powered": True,
                    "agent_info": {"type": "sql", "model": app_config.llm.default_model},
                    "sql_generation": sql_result
                }
                
            elif agent_type == 'analysis':
                # 使用分析代理分析数据
                data_content = data.get('data_content', '')
                analysis_result = agent.analyze_data(data_content, raw_user_prompt)
                response_body = {
                    "adk_powered": True,
                    "agent_info": {"type": "analysis", "model": app_config.llm.default_model},
                    "analysis": analysis_result
                }
            
            resp = make_response(response_body)
            resp.set_cookie('x-session-id', session_id,
                            httponly=True, secure=True, max_age=1800)
            return resp
            
        except Exception as e:
            import traceback
            import logging
            
            # 配置日志记录
            logging.basicConfig(level=logging.ERROR)
            logger = logging.getLogger(__name__)
            
            # 记录完整的错误堆栈信息
            error_traceback = traceback.format_exc()
            logger.error(f"API /api/adk-chat 处理失败:\n{error_traceback}")
            
            # 也打印到控制台，方便调试
            print(f"❌ /api/adk-chat 接口异常:")
            print(f"错误信息: {str(e)}")
            print(f"完整堆栈:\n{error_traceback}")
            
            return jsonify({
                "error": f"ADK {agent_type.upper()} Agent处理查询时发生错误: {str(e)}",
                "adk_powered": True,
                "agent_info": {"type": agent_type, "error": str(e)},
                "debug_info": {
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "traceback": error_traceback
                }
            }), 500

    # ADK分析建议API端点
    @app.route('/api/adk-analysis', methods=['POST'])
    def adk_analysis():
        """获取ADK数据分析建议
        ---
        tags:
          - ADK Analysis
        summary: ADK数据分析建议
        description: 基于查询和数据结果提供专业的分析建议
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                query:
                  type: string
                  description: 原始查询
                  example: "销售趋势分析"
                data_result:
                  type: string
                  description: 数据结果
                  example: "月份,销售额\n1月,100000\n2月,120000"
        responses:
          200:
            description: 成功返回分析建议
            schema:
              type: object
              properties:
                analysis:
                  type: string
                  description: 分析建议
                adk_powered:
                  type: boolean
                  description: 是否由ADK提供支持
          500:
            description: 内部服务器错误
        """
        bi_agent = adk_agents.get('bi_agent')
        if not bi_agent:
            return jsonify({
                "error": "ADK BI Agent未能成功初始化",
                "adk_powered": True
            }), 500
        
        try:
            data = request.get_json() or {}
            query = data.get('query', '')
            data_result = data.get('data_result', '')
            
            analysis = bi_agent.get_analysis_suggestion(query, data_result)
            
            return jsonify({
                "analysis": analysis,
                "adk_powered": True
            })
            
        except Exception as e:
            return jsonify({
                "error": f"生成分析建议时发生错误: {str(e)}",
                "adk_powered": True
            }), 500

    # SQL执行API端点 - 改为使用ADK SQL Agent
    @app.route('/api/execute_sql', methods=['POST'])
    @swag_from('../doc/sql_exec.yaml')
    def execute_sql():
        """执行SQL查询 - ADK实现"""
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求体不能为空"}), 400
            
        session_id = request.cookies.get('x-session-id') or time.strftime("%Y%m%d%H%M%S", time.localtime())
        sql = data.get('sql', 'select 1')
        
        # 获取SQL代理
        sql_agent = adk_agents.get('sql_agent')
        if not sql_agent:
            # 如果SQL代理不可用，回退到传统执行方式
            file_path = data.get('file_path') or store.get_csv_path(session_id)
            results = execute_sql_to_csv(sql, file_path, app_config.database.to_dict())
            return jsonify({"csv": results})
        
        try:
            # 使用ADK SQL代理执行查询
            result = sql_agent.sql_executor(sql, session_id)
            if result.get("success"):
                return jsonify({"csv": result.get("content", "")})
            else:
                return jsonify({"error": result.get("content", "SQL执行失败")}), 500
                
        except Exception as e:
            return jsonify({"error": f"SQL执行错误: {str(e)}"}), 500

    @app.route('/api/download_file', methods=['GET'])
    @swag_from('../doc/csv_download.yaml')
    def download_csv():
        """下载CSV文件 (保持原有实现)"""
        session_id = request.cookies.get('x-session-id') or time.strftime("%Y%m%d%H%M%S", time.localtime())
        file_path = request.args.get('file_path')
        
        if not file_path:
            # 如果没有指定文件路径，使用默认路径
            file_path = store.get_csv_path(session_id)
            
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        file_name = os.path.basename(file_path)
        return send_file(file_path, as_attachment=True, download_name=file_name)

    # 系统状态端点
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """系统健康检查
        ---
        tags:
          - System
        summary: 系统健康检查
        description: 检查系统各组件的状态
        responses:
          200:
            description: 系统正常
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "healthy"
                adk_available:
                  type: boolean
                  description: ADK是否可用
                components:
                  type: object
                  properties:
                    database:
                      type: string
                      example: "connected"
                    adk_agents:
                      type: object
                      description: ADK代理状态
                config:
                  type: object
                  description: 配置验证状态
        """
        adk_status = {
            "bi_agent": "ready" if adk_agents.get('bi_agent') else "failed",
            "sql_agent": "ready" if adk_agents.get('sql_agent') else "failed",
            "analysis_agent": "ready" if adk_agents.get('analysis_agent') else "failed"
        }
        
        health_status = {
            "status": "healthy",
            "adk_available": any(agent is not None for agent in adk_agents.values()),
            "components": {
                "database": "connected" if app_config.validate() else "not_configured",
                "adk_agents": adk_status,
                "legacy_chat": "available_as_fallback"  # 标记为后备方案
            },
            "config": {
                "database_valid": app_config.database.host is not None,
                "llm_configured": bool(app_config.llm.get_api_key()),
                "server_config": f"{app_config.server.host}:{app_config.server.port}"
            }
        }
        return jsonify(health_status)

    # ADK代理状态端点
    @app.route('/api/adk-status', methods=['GET'])
    def adk_status():
        """ADK代理状态信息
        ---
        tags:
          - ADK System
        summary: ADK代理状态
        description: 获取ADK代理的详细状态信息
        responses:
          200:
            description: ADK状态信息
            schema:
              type: object
              properties:
                agents:
                  type: object
                  description: 各代理状态
                config:
                  type: object
                  description: 配置信息
                capabilities:
                  type: array
                  description: 系统能力
        """
        capabilities = []
        
        if adk_agents.get('bi_agent'):
            capabilities.extend(['natural_language_query', 'sql_generation', 'data_analysis'])
        if adk_agents.get('sql_agent'):
            capabilities.extend(['sql_optimization', 'query_validation'])
        if adk_agents.get('analysis_agent'):
            capabilities.extend(['chart_recommendation', 'data_validation', 'insights_generation'])
        
        return jsonify({
            "agents": {
                name: {
                    "status": "ready" if agent else "failed",
                    "model": app_config.llm.default_model if agent else None,
                    "description": getattr(agent, 'agent', {}).get('description', '') if agent else "Agent not initialized"
                }
                for name, agent in adk_agents.items()
            },
            "config": {
                "model": app_config.llm.default_model,
                "api_configured": bool(app_config.llm.get_api_key()),
                "database_configured": app_config.validate()
            },
            "capabilities": list(set(capabilities))
        })

    # 会话管理 API 端点
    @app.route('/api/session/<session_id>/clear', methods=['POST'])
    def clear_session(session_id):
        """清除会话历史记录
        ---
        tags:
          - Session Management
        summary: 清除会话历史
        description: 清除指定会话的所有历史记录
        parameters:
          - name: session_id
            in: path
            required: true
            type: string
            description: 会话ID
        responses:
          200:
            description: 清除成功
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "会话历史已清除"
                session_id:
                  type: string
          500:
            description: 清除失败
        """
        try:
            bi_agent = adk_agents.get('bi_agent')
            if bi_agent:
                bi_agent.clear_session(session_id)
            else:
                store.clear_session(session_id)
            
            return jsonify({
                "message": "会话历史已清除",
                "session_id": session_id
            })
        except Exception as e:
            return jsonify({
                "error": f"清除会话历史失败: {str(e)}"
            }), 500

    @app.route('/api/session/<session_id>/history', methods=['GET'])
    def get_session_history(session_id):
        """获取会话历史记录
        ---
        tags:
          - Session Management
        summary: 获取会话历史
        description: 获取指定会话的历史记录
        parameters:
          - name: session_id
            in: path
            required: true
            type: string
            description: 会话ID
        responses:
          200:
            description: 历史记录
            schema:
              type: object
              properties:
                session_id:
                  type: string
                history:
                  type: array
                  items:
                    type: object
                    properties:
                      role:
                        type: string
                        enum: ["user", "assistant"]
                      content:
                        type: string
                message_count:
                  type: integer
        """
        try:
            bi_agent = adk_agents.get('bi_agent')
            if bi_agent:
                history = bi_agent.get_session_history(session_id)
            else:
                history = store.get_session_history(session_id)
            
            return jsonify({
                "session_id": session_id,
                "history": [{"role": msg.role, "content": msg.content} for msg in history],
                "message_count": len(history)
            })
        except Exception as e:
            return jsonify({
                "error": f"获取会话历史失败: {str(e)}"
            }), 500

    @app.route('/api/session/<session_id>/summary', methods=['GET'])
    def get_session_summary(session_id):
        """获取会话摘要信息
        ---
        tags:
          - Session Management
        summary: 获取会话摘要
        description: 获取指定会话的摘要统计信息
        parameters:
          - name: session_id
            in: path
            required: true
            type: string
            description: 会话ID
        responses:
          200:
            description: 会话摘要
            schema:
              type: object
              properties:
                session_id:
                  type: string
                message_count:
                  type: integer
                conversation_length:
                  type: integer
                has_sql_queries:
                  type: boolean
        """
        try:
            bi_agent = adk_agents.get('bi_agent')
            if bi_agent:
                summary = bi_agent.get_session_summary(session_id)
            else:
                history = store.get_session_history(session_id)
                summary = {
                    "session_id": session_id,
                    "message_count": len(history),
                    "conversation_length": sum(len(msg.content) for msg in history),
                    "has_sql_queries": any("<analysis>需要SQL</analysis>" in msg.content for msg in history if msg.role == "assistant")
                }
            
            return jsonify(summary)
        except Exception as e:
            return jsonify({
                "error": f"获取会话摘要失败: {str(e)}"
            }), 500


def run_server():
    """启动服务器"""
    app = create_app()
    
    print("🚀 启动 Awesome AI 服务...")
    print(f"📊 Database: {app_config.database.host or 'not configured'}")
    print(f"🤖 ADK Model: {app_config.llm.default_provider}/{app_config.llm.default_model}")
    print(f"🌐 Server URL: {app_config.server.server_url}")
    print(f"📚 API文档: {app_config.server.server_url}/apidocs/")
    
    app.run(
        host=app_config.server.host,
        port=app_config.server.port,
        debug=app_config.server.debug
    ) 