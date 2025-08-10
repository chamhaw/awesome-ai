import json
import os
from typing import List

from dashscope.api_entities.dashscope_response import Message

from chat_bi.knowledge import get_knowledge
from app.prompt.manager import prompt_manager

STORAGE_DIR = 'storage'

def json_to_objects(json_str):
    """将 JSON 字符串转换为 Message 对象列表"""
    raw_list = json.loads(json_str)
    return [Message(**item) for item in raw_list]

def prompt_prepare(raw_user_prompt: str, system_prompt: str, session_id: str, history: List[Message]):
    """准备对话提示词，包括历史记录管理和知识库获取"""
    session_dir = os.path.join(STORAGE_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    if not history:
        try:
            with open(os.path.join(session_dir, 'history.json'), 'r', encoding='utf-8') as f:
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
    
    # 如果 system_prompt 为空，使用管理器渲染模板
    if not system_prompt:
        system_prompt = prompt_manager.render("gen_sql", knowledge=knowledge)
    else:
        if '{knowledge}' in system_prompt:
            try:
                system_prompt = system_prompt.format(knowledge=knowledge)
            except KeyError as e:
                raise ValueError(f"Missing template variable: {e}")
    
    return system_prompt, history

def store_context(session_id: str, history: List[Message]):
    """存储对话上下文到文件"""
    # 将 response 写入文件
    session_dir = os.path.join(STORAGE_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    with open(os.path.join(session_dir, 'history.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(history, indent=2, ensure_ascii=False))

def get_csv_path(session_id: str):
    """获取会话的 CSV 输出文件路径"""
    return os.path.join(STORAGE_DIR, session_id, 'output.csv')

def get_session_dir(session_id: str):
    """获取会话目录路径"""
    return os.path.join(STORAGE_DIR, session_id)

def clear_session(session_id: str):
    """清除会话历史记录"""
    session_dir = get_session_dir(session_id)
    history_file = os.path.join(session_dir, 'history.json')
    if os.path.exists(history_file):
        os.remove(history_file)

def get_session_history(session_id: str) -> List[Message]:
    """获取会话历史记录"""
    session_dir = get_session_dir(session_id)
    history_file = os.path.join(session_dir, 'history.json')
    
    if not os.path.exists(history_file):
        return []
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history_json = f.read()
            if history_json:
                return json_to_objects(history_json)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return [] 