import os
from typing import List, Union, Generator

import dashscope
from dashscope.api_entities.dashscope_response import Message, GenerationResponse
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels

model_name = DashScopeGenerationModels.QWEN_MAX

dashscope_llm = DashScope(
        model_name=model_name, api_key=os.environ["DASHSCOPE_API_KEY"]
)

def call(system_prompt: str, user_input: str, knowledge: str) -> Union[str, List]:
    messages: List[Message] = [
        Message(role='system', content=system_prompt),
        Message(role='user', content=(user_input + ' ' + knowledge)),
    ]
    response:Union[GenerationResponse, Generator[GenerationResponse, None, None]] = dashscope.Generation.call(
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        model=model_name,
        messages=messages,
        result_format='text'
    )
    if response.status_code != 200 or response.code != "":
        pass

    if response.output.choices:
        return response.output.choices[0].message.content
    else:
        return response.output.text