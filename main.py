import os
import re
import time
from urllib.parse import quote

from flask import Flask, request, jsonify, make_response, send_file
from dotenv import load_dotenv
from flasgger import Swagger, swag_from

from app.prompt import system_prompts
from app.agent import store
from app.cli import CLIChat
from app.tool.sql import execute_sql_to_csv
from app.integrations.adk_agent import create_bi_agent, BIChatAgent
from bs4 import BeautifulSoup

flask_app = Flask(__name__)

swagger = Swagger(flask_app)  # 初始化 Swagger

# 可选：自定义 Swagger 配置
flask_app.config['SWAGGER'] = {
    "title": "Awesome AI 接口文档",
    "version": "1.0",
    "description": "API Documentation - 集成了Google ADK的BI聊天助手",
    "specs_route": "/apidocs/",  # Swagger UI 的访问路径
    "headers": [],  # 可添加全局请求头（如认证 Token）
}

DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

SERVER_URL = os.getenv('SERVER_URL') or 'http://localhost:5050'
DOWNLOAD_API = "/api/download_file"

# 加载 .env 文件
load_dotenv()
chat = CLIChat()

# 初始化 ADK BI Agent
try:
    adk_bi_agent = create_bi_agent()
    print("✅ ADK BI Agent 初始化成功")
except Exception as e:
    adk_bi_agent = None
    print(f"⚠️ ADK BI Agent 初始化失败: {e}")

# 新增生成SQL的API端点
@flask_app.route('/api/chat', methods=['POST'])
@swag_from('doc/chat.yaml')
def generate_sql():
    """生成SQL语句
    """
    data = request.get_json() or {}
    raw_user_prompt = data.get('user_prompt')
    provider = data.get('provider') or '2'
    model = data.get('model') or 'deepseek-reasoner'
    clear = data.get('clear') or False
    if clear or not request.cookies.get('x-session-id'):
        chat.reset()
    if provider and provider != chat.current_provider:
        chat.switch_provider(provider)
    if model and model != chat.current_model:
        chat.switch_model(model)
    history = data.get('history')
    if history:
        chat.history = history
    system_prompt, history = store.prompt_prepare(raw_user_prompt, system_prompts.intention, chat.session_id, history)
    response = chat.invoker.call(
        model=chat.current_model,
        system_prompt=system_prompt,
        user_input=raw_user_prompt,
        history=history,
        stream=False
    )
    response_body = {}
    if not "<analysis>需要SQL</analysis>" in response:
        response_body['message'] = response
        resp = make_response(response_body)
        resp.set_cookie('x-session-id', chat.session_id,
                        httponly=True,
                        secure=True,
                        max_age=1800)
        return resp
    system_prompt = data.get('system_prompt')
    if system_prompt:
        chat.set_system_prompt(system_prompt)

    response, sql, sql_result, chart_type = chat.process_sql_query(raw_user_prompt)

    
    if not sql and "<hint>" in response:
        # 提取 <hint> 中的提示信息
        soup = BeautifulSoup(response, 'html.parser')
        hint_tag = soup.find('hint')
        response_body['message'] = hint_tag.get_text(strip=False) if hint_tag else response
    else:
        response_body['sql'] = sql
        if not sql_result:
            response_body['message'] = "未查到任何统计数据，请重新调整查询条件"
        else:
            response_body['chart_type'] = chart_type
            response_body['csv'] = sql_result
            response_body['file_path'] = chat.csv_path
            response_body['file_link'] = f"{SERVER_URL}/{DOWNLOAD_API}?file_path={quote(chat.csv_path)}"
    
    resp = make_response(response_body)
    resp.set_cookie('x-session-id', chat.session_id,
                    httponly=True,
                    secure=True,
                    max_age= 1800)

    return resp


# 新增ADK BI聊天API端点
@flask_app.route('/api/adk-chat', methods=['POST'])
def adk_chat():
    """基于Google ADK的BI聊天接口
    ---
    tags:
      - AI Chat
    summary: ADK BI聊天助手
    description: 使用Google ADK构建的智能BI数据分析助手
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
              example: "查询销售数据"
            session_id:
              type: string
              description: 会话ID (可选)
              example: "20240101120000"
            clear:
              type: boolean
              description: 是否清除历史
              default: false
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
      500:
        description: 内部服务器错误
    """
    if not adk_bi_agent:
        return jsonify({
            "error": "ADK BI Agent未能成功初始化",
            "message": "请检查GEMINI_API_KEY环境变量是否设置正确"
        }), 500
    
    try:
        data = request.get_json() or {}
        raw_user_prompt = data.get('user_prompt', '')
        session_id = data.get('session_id') or request.cookies.get('x-session-id')
        clear = data.get('clear', False)
        
        if clear:
            session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        
        if not session_id:
            session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        
        # 使用ADK Agent处理查询
        response, sql, csv_results, chart_type, csv_path = adk_bi_agent.process_query(
            raw_user_prompt, session_id
        )
        
        response_body = {
            "adk_powered": True,
            "message": response
        }
        
        if sql:
            response_body['sql'] = sql
            
        if csv_results:
            response_body['csv'] = csv_results
            response_body['chart_type'] = chart_type
            response_body['file_path'] = csv_path
            response_body['file_link'] = f"{SERVER_URL}/{DOWNLOAD_API}?file_path={quote(csv_path)}"
        
        resp = make_response(response_body)
        resp.set_cookie('x-session-id', session_id,
                        httponly=True,
                        secure=True,
                        max_age=1800)
        
        return resp
        
    except Exception as e:
        return jsonify({
            "error": f"ADK处理查询时发生错误: {str(e)}",
            "adk_powered": True
        }), 500


# 新增ADK分析建议API端点
@flask_app.route('/api/adk-analysis', methods=['POST'])
def adk_analysis():
    """获取ADK数据分析建议
    ---
    tags:
      - AI Analysis
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
    if not adk_bi_agent:
        return jsonify({
            "error": "ADK BI Agent未能成功初始化",
            "adk_powered": True
        }), 500
    
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        data_result = data.get('data_result', '')
        
        analysis = adk_bi_agent.get_analysis_suggestion(query, data_result)
        
        return jsonify({
            "analysis": analysis,
            "adk_powered": True
        })
        
    except Exception as e:
        return jsonify({
            "error": f"生成分析建议时发生错误: {str(e)}",
            "adk_powered": True
        }), 500


# 新增执行SQL的API端点
@flask_app.route('/api/execute_sql', methods=['POST'])
@swag_from('doc/sql_exec.yaml')
def execute_sql():
    """执行SQL查询
    """
    session_id = request.cookies.get('x-session-id') or time.strftime("%Y%m%d%H%M%S", time.localtime())
    sql = request.json.get('sql') or 'select 1'
    file_path = request.json.get('file_path') or store.get_csv_path(session_id)
    results = execute_sql_to_csv(sql, file_path, DB_CONFIG)
    return jsonify({"csv": results})


# 新增下载CSV文件的API端点
@flask_app.route(DOWNLOAD_API, methods=['GET'])
@swag_from('doc/csv_download.yaml')
def download_csv():
    """下载CSV文件
    """
    session_id = request.cookies.get('x-session-id') or time.strftime("%Y%m%d%H%M%S", time.localtime())
    requested_path = request.args.get('file_path')
    storage_root = os.path.abspath(os.path.join(os.getcwd(), 'storage'))
    session_dir = os.path.abspath(os.path.join(storage_root, session_id))
    candidate_path = os.path.abspath(requested_path) if requested_path else os.path.abspath(store.get_csv_path(session_id))
    # 仅允许下载当前会话目录下的文件，防止路径穿越
    if not candidate_path.startswith(session_dir + os.sep):
        return jsonify({"error": "Access denied"}), 403
    if not os.path.exists(candidate_path):
        return jsonify({"error": "File not found"}), 404
    file_name = os.path.basename(candidate_path)
    return send_file(candidate_path, as_attachment=True, download_name=file_name)


# 健康检查端点
@flask_app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查
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
                adk_agent:
                  type: string
                  example: "initialized"
    """
    health_status = {
        "status": "healthy",
        "adk_available": adk_bi_agent is not None,
        "components": {
            "database": "connected" if all(DB_CONFIG.values()) else "not_configured",
            "adk_agent": "initialized" if adk_bi_agent else "failed"
        }
    }
    return jsonify(health_status)


# 启动Flask应用
def main():
    print("🚀 启动 Awesome AI 服务...")
    print(f"📊 Database: {DB_CONFIG.get('host', 'not configured')}")
    print(f"🤖 ADK BI Agent: {'✅ Ready' if adk_bi_agent else '❌ Failed'}")
    print(f"🌐 Server URL: {SERVER_URL}")
    print(f"📚 API文档: {SERVER_URL}/apidocs/")
    
    # 开发环境配置
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    print(f"🔧 Debug Mode: {'✅ Enabled' if debug_mode else '❌ Disabled'}")
    print(f"🔧 Environment: {flask_env}")
    
    flask_app.run(
        host='0.0.0.0', 
        port=int(os.getenv('FLASK_PORT', 5050)),
        debug=debug_mode,
        use_reloader=debug_mode,  # 启用文件变化监控
        threaded=True  # 启用多线程支持
    )


if __name__ == "__main__":
    main()