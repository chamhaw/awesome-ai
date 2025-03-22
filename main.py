import json
import os
import uuid

from dashscope.api_entities.dashscope_response import Message
from flask import Flask, request, jsonify, make_response, send_file
from dotenv import load_dotenv
import mysql.connector
from llama_index.core.schema import NodeWithScore

import app.prompt.system_prompts
from app.agent import prepare_prompt
from app.agent.knowledge import get_knowledge
from app.tool.sql import execute_sql_to_csv

flask_app = Flask(__name__)

# 加载 .env 文件
load_dotenv()

from typing import List, Union
from app import llm
from app.prompt import ddl
from app.tool import extractor
from app.agent.indexer import retrieve

# 数据库配置从环境变量读取
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}
llama_index = {
    'name': os.getenv('DASHSCOPE_LLAMA_INDEX_NAME')
}
csv_file = os.getenv("CSV_FILE_PATH")


# 新增生成SQL的API端点
@flask_app.route('/api/generate_sql', methods=['POST'])
def generate_sql():
    session_id = request.cookies.get('x-session-id') or uuid.uuid4().hex
    raw_user_prompt = request.json.get('user_prompt')
    csv_path = request.json.get('csv_path') or csv_file
    history = request.json.get('history') or []
    system_prompt, user_prompt, history = prepare_prompt.prompt_prepare(
        raw_user_prompt, request.json.get('system_prompt'),
        session_id,
        history)
    response = llm.deepseek_r1_call(system_prompt, user_prompt, history)
    sql = extractor.extract_sql_from_markdown(response)
    response_body = {}
    if sql:
        response_body['sql'] = sql[0]
    if "需要您补充以下信息" in response:
        response_body['message'] = response
    else:
        results = execute_sql_to_csv(request.json.get('sql'), csv_path, db_config)
        if not results:
            response_body['message'] = "未查到任何统计数据，请重新调整查询条件"
        response_body['csv'] = results
        response_body['file_path'] = csv_path
    resp = make_response(response_body)
    resp.set_cookie('x-session-id', session_id,
                    httponly=True,
                    secure=True,
                    max_age= 1800)
    # 将 response 写入文件
    with open(f'context/{session_id}', 'w') as f:
        history.append(Message(role='user', content=raw_user_prompt))
        history.append(Message(role='assistant', content=response))
        f.write(json.dumps(history, indent=2))

    return resp

# 新增执行SQL的API端点
@flask_app.route('/api/execute_sql', methods=['POST'])
def execute_sql():
    sql = request.json.get('sql')
    file_path = request.args.get('file_path') or csv_file
    results = execute_sql_to_csv(request.json.get('sql'), file_path ,db_config)
    return jsonify({"csv": results})



# 新增下载CSV文件的API端点
@flask_app.route('/api/download_file', methods=['POST'])
def download_csv():
    file_path = request.args.get('file_path') or csv_file
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    file_name = os.path.basename(file_path)
    return send_file(file_path, as_attachment=True, download_name=file_name)

# 启动Flask应用
if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=5050, debug=True)