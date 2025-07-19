import os


def retrieve_knowledge_from_local(dir_path: str):
    """
    遍历 knowledge 目录下的所有 md 文件，提取并拼接内容
    :param dir_path: 知识库目录路径
    :return: 拼接后的知识内容
    """
    knowledge = ""
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".md") or file.endswith(".sql"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        knowledge += "\n\n\n"
                        knowledge += f.read()
                except (FileNotFoundError, UnicodeDecodeError) as e:
                    print(f"警告：读取文件 {file_path} 时出错：{e}")
                    continue
    return knowledge


def get_knowledge(user_prompt: str):
    """
    获取知识库内容，支持本地知识库检索
    :param user_prompt: 用户提示词
    :return: 知识库内容
    """
    # rag_knowledge = retrieve_knowledge_from_rag(user_prompt)
    local_knowledge = retrieve_knowledge_from_local("knowledge")
    return local_knowledge
    # return rag_knowledge +'\n'+ local_knowledge + '\n' 