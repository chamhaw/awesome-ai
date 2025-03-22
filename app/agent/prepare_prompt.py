import json
from typing import List

from dashscope.api_entities.dashscope_response import Message

from app.agent.knowledge import get_knowledge

from app.prompt import system_prompts


def prompt_prepare(raw_user_prompt: str, system_prompt: str, session_id: str, history: List[Message]):
    if not history:
        try:
            with open(f'context/{session_id}', 'r') as f:
                history_json = f.read()
                if history_json:
                    history = json.loads(history_json)
        except FileNotFoundError:
            pass
    if len(history) > 20:
        history = history[-20:]
    knowledge = get_knowledge(raw_user_prompt)
    if len(knowledge) > 100000:
        knowledge = knowledge[-100000:]
    if not system_prompt:
        system_prompt = system_prompts.gen_sql.format(knowledge=knowledge)
    user_prompt = ('请结合以下领域知识和背景，生成 MySQL 8.0 直接运行的查询语句:\n' + raw_user_prompt)
    return system_prompt, user_prompt, history
