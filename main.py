import os
import time
from urllib.parse import quote

from dashscope.api_entities.dashscope_response import Message
from flask import Flask, request, jsonify, make_response, send_file
from dotenv import load_dotenv
from flasgger import Swagger, swag_from

from app.agent import store
from app.tool.sql import execute_sql_to_csv

flask_app = Flask(__name__)

swagger = Swagger(flask_app)  # 初始化 Swagger

# 可选：自定义 Swagger 配置
flask_app.config['SWAGGER'] = {
    "title": "Awesome AI 接口文档",
    "version": "1.0",
    "description": "API Documentation",
    "specs_route": "/apidocs/",  # Swagger UI 的访问路径
    "headers": [],  # 可添加全局请求头（如认证 Token）
}

from app import llm
from app.tool import extractor

DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

SERVER_URL = os.getenv('SERVER_URL') or 'http://localhost:5050'
DOWNLOAD_API = "/api/download_file"

# 新增生成SQL的API端点
@flask_app.route('/api/chat', methods=['POST'])
@swag_from('doc/chat.yaml')
def generate_sql():
    """生成SQL语句
    """
    session_id = request.cookies.get('x-session-id') or time.strftime("%Y%m%d%H%M%S", time.localtime())
    raw_user_prompt = request.json.get('user_prompt')
    csv_path = request.json.get('csv_path') or store.get_csv_path(session_id)
    history = request.json.get('history') or []
    system_prompt, user_prompt, history = store.prompt_prepare(
        raw_user_prompt, request.json.get('system_prompt'),
        session_id,
        history)
    response = llm.qwen_qwq_call(system_prompt, user_prompt, history)
    sqls = extractor.extract_sql_queries(response)
    response_body = {}
    if not sqls or "需要您补充以下信息" in response:
        response_body['message'] = response
    else:
        if len(sqls) > 1:
            print("有多个SQL语句, 可能需要调整 prompt")
            for i in range(len(sqls)):
                print(f'sql: {i + 1}-{sqls[i]}\n')
        response_body['sql'] = sqls[0]
        results = execute_sql_to_csv(response_body['sql'], csv_path, DB_CONFIG)
        if not results:
            response_body['message'] = "未查到任何统计数据，请重新调整查询条件"
        else:
            response_body['csv'] = results
            response_body['file_path'] = csv_path
            response_body['file_link'] = f"{SERVER_URL}/{DOWNLOAD_API}?file_path={quote(csv_path)}"

    history.append(Message(role='user', content=raw_user_prompt))
    history.append(Message(role='assistant', content=response))
    response_body['history'] = history

    store.store_context(session_id, history)
    
    resp = make_response(response_body)
    resp.set_cookie('x-session-id', session_id,
                    httponly=True,
                    secure=True,
                    max_age= 1800)

    return resp

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
    file_path = request.args.get('file_path') or store.get_csv_path(session_id)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    file_name = os.path.basename(file_path)
    return send_file(file_path, as_attachment=True, download_name=file_name)

# 启动Flask应用
if __name__ == "__main__":
    # 加载 .env 文件
    load_dotenv()
    flask_app.run(host='0.0.0.0', port=5050, debug=True)