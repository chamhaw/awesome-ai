import os
from typing import List

from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.schema import NodeWithScore, Document
from llama_index.indices.managed.dashscope import DashScopeCloudIndex
from llama_index.indices.managed.dashscope.retriever import DashScopeCloudRetriever
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels

model_name = DashScopeGenerationModels.QWEN_MAX

def dashscope_llm():
    return DashScope(
        model_name=model_name, api_key=os.environ["DASHSCOPE_API_KEY"]
    )

# create a new index
def initialize_index(index_name:str, documents: List[Document]) -> DashScopeCloudIndex:
    index = DashScopeCloudIndex.from_documents(
        documents,
        index_name,
        verbose=True,
    )
    return index
def get_index(index_name: str) -> DashScopeCloudIndex:
    index = DashScopeCloudIndex(index_name)
    return index

def get_retriever(index_name: str) -> BaseRetriever:
    index = DashScopeCloudIndex(index_name)
    return index.as_retriever()


# convert from index
def get_retriever_from_index(index: DashScopeCloudIndex) -> BaseRetriever:
    return index.as_retriever()

# or initialize from DashScopeCloudRetriever

def initialize_retriever(index_name: str) -> BaseRetriever:
    retriever = DashScopeCloudRetriever(index_name)
    return retriever

def retrieve(index_name: str, query: str) -> List[NodeWithScore]:
    retriever = get_retriever(index_name)
    return retriever.retrieve(query)

def get_query_engine(index_name: str) -> BaseQueryEngine:
    index = get_index(index_name)
    dashscope_llm = DashScope(
        model_name=DashScopeGenerationModels.QWEN_MAX, api_key=os.environ["DASHSCOPE_API_KEY"]
    )
    query_engine: BaseQueryEngine = index.as_query_engine(llm=dashscope_llm)
    return query_engine

# add documents to index
def add_documents(index_name: str, document: Document)-> None:
    index = get_index(index_name)
    index.insert(document)
# delete documents from index
def delete_documents(index_name: str, doc_ids: List[str]) -> None:
    index = get_index(index_name)
    index.delete_ref_doc(doc_ids)
