from app.agent.rag import retrieve_knowledge_from_rag, retrieve_knowledge_from_local


def get_knowledge(user_prompt: str):
    # rag_knowledge = retrieve_knowledge_from_rag(user_prompt)
    local_knowledge = retrieve_knowledge_from_local("knowledge")
    return local_knowledge
    # return rag_knowledge +'\n'+ local_knowledge + '\n'
