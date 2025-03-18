from typing import List

from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.schema import NodeWithScore
from llama_index.indices.managed.dashscope import DashScopeCloudIndex


def get_retriever(index_name: str) -> BaseRetriever:
    index = DashScopeCloudIndex(index_name)
    return index.as_retriever()

def retrieve(index_name: str, query: str) -> List[NodeWithScore]:
    retriever = get_retriever(index_name)
    return retriever.retrieve(query)