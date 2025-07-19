from typing import List, Dict, Any

from one_agent.app.agents.bi_assistant.tools.sql_executor import sql_executor
from one_agent.app.rag.knowledge_vault import kn_vault as kn_service
from one_agent.app.rag.logging_decorator import log_args

global_profile="test"

def get_content(search_results: List[List[Dict[str, Any]]]) -> List[str]:
    contents = []
    for entity_results in search_results:
        for item in entity_results:
            if "content" in item:
                contents.append(item["content"])

    return contents

@log_args()
def entity_retrieve_search(entity_slot: list[str]) -> list[str]:
    result = kn_service.batch_hybrid_search(global_profile,entity_slot, "knowledge")
    return get_content(result)

@log_args()
def table_schema_retrieve_search(entity_slot: list[str]) -> list[str]:
    result = kn_service.batch_hybrid_search(global_profile, entity_slot, "schema")
    return get_content(result)

@log_args(log_result=False)
def table_schema_retrieve() -> list[str]:
    return sql_executor.get_all_tables_ddl().values()

@log_args()
def qa_retrieve_search(entity_slot: list[str]) -> list[str]:
    result = kn_service.batch_hybrid_search(global_profile, entity_slot, "sample")
    return get_content(result)

@log_args()
def cot_retrieve_search(q: str) -> list[str]:
    result = kn_service.batch_hybrid_search(global_profile, [q], "analysis")
    return get_content(result)
