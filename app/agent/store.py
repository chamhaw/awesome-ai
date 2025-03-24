import json
import os
from typing import List

from dashscope.api_entities.dashscope_response import Message

from app.agent.knowledge import get_knowledge

from app.prompt import system_prompts

STORAGE_DIR = 'storage'

def json_to_objects(json_str):
    raw_list = json.loads(json_str)
    return [Message(**item) for item in raw_list]
def prompt_prepare(raw_user_prompt: str, system_prompt: str, session_id: str, history: List[Message]):
    session_dir = os.path.join(STORAGE_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    if not history:
        try:
            with open(os.path.join(session_dir, 'history.json'), 'r') as f:
                history_json = f.read()
                if history_json:
                    history = json_to_objects(history_json)
        except FileNotFoundError:
            # 如果文件不存在，则创建一个空的历史记录列表
            history = []
    if len(history) > 30:
        # 修改历史截取逻辑，保留第一条和最后29条, 此处认为第一条是用户原始需求，更为重要。
        history = [history[0]] + history[-29:]
    knowledge = get_knowledge(raw_user_prompt)
    if len(knowledge) > 100000:
        knowledge = knowledge[-100000:]
    if not system_prompt:
        system_prompt = system_prompts.gen_sql.format(knowledge=knowledge)
    user_prompt = raw_user_prompt
    if not history:
        user_prompt = '请结合领域知识和背景，生成 MySQL 8.0 直接运行的查询语句.\n' + raw_user_prompt
    return system_prompt, user_prompt, history

def store_context(session_id: str, history: List[Message]):
    # 将 response 写入文件
    with open(os.path.join(STORAGE_DIR, session_id, 'history.json'), 'w') as f:
        f.write(json.dumps(history, indent=2, ensure_ascii=False))

def get_csv_path(session_id: str):
    return os.path.join(STORAGE_DIR, session_id, 'output.csv')