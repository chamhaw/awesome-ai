import json
import os
from typing import List, Union, Generator, Tuple
import time

import dashscope
from dashscope.api_entities.dashscope_response import Message, GenerationResponse
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from openai.types.chat import ChatCompletion

model_name = DashScopeGenerationModels.QWEN_MAX

def qwen_call(system_prompt: str, user_input: str, knowledge: str) -> Union[str, List]:
    start_time = time.time()
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
        print(response.status_code)
        print(response.code)
        print(response.message)
        return ""

    if response.output.choices:
        result = response.output.choices[0].message.content
    else:
        result = response.output.text
    end_time = time.time()
    print(f"Qwen调用耗时: {end_time - start_time:.2f}秒")
    return result

# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
def deepseek_r1_call(system_prompt: str, user_input: str, history: List[Message] = None) -> str:
    start_time = time.time()
    if history is None:
        history = []
    messages = [Message(role='system', content=system_prompt)]
    messages.extend(history)
    current_user_message = Message(role='user', content=user_input)
    messages.append(current_user_message)

    client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
    print(f"calling to deepseek R1...\n messages:{json.dumps(messages, indent=2, ensure_ascii=False)}\n")
    response: ChatCompletion = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        stream=False
    )

    reply = response.choices[0].message.content
    end_time = time.time()
    print(f"DeepSeek R1调用耗时: {end_time - start_time:.2f}秒")
    return reply
