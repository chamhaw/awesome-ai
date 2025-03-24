import os
from typing import List

from llama_index.core.schema import NodeWithScore

from app.agent.indexer import retrieve

DASHSCOPE_LLAMA_INDEX_NAME = "test_index"
def retrieve_knowledge_from_rag(user_prompt: str):
    data: List[NodeWithScore] = retrieve(DASHSCOPE_LLAMA_INDEX_NAME, user_prompt)
    knowledge = ""
    for d in data:
        knowledge += d.get_text()

    return knowledge


def retrieve_knowledge_from_local(dir_path: str):
    """
    遍历 knowledge 目录下的所有 md 文件，提取并拼接内容
    :return:
    """
    knowledge = ""
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".md") or file.endswith(".sql"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    knowledge += "\n\n\n"
                    knowledge += f.read()
    return knowledge