import json
import os
from typing import List
import time

from dashscope.api_entities.dashscope_response import Message
from llama_index.llms.dashscope import DashScopeGenerationModels
from openai import OpenAI

model_name = DashScopeGenerationModels.QWEN_MAX

class OpenAIInvoker:
    def __init__(self, api_key: str = os.getenv("OPENAI_API_KEY"), base_url: str = "https://api.openai.com/v1"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
    def call(self, model: str, system_prompt: str, user_input: str, 
             history: List[Message] = None, stream: bool = False) -> str:
        start_time = time.time()
        
        if history is None:
            history = []
            
        messages = [Message("system", system_prompt)]
        for msg in history:
            messages.append(Message(msg.role, msg.content))
        messages.append(Message("user", user_input))
        
        print(f"调用 {model}...\n messages:{json.dumps(messages, indent=2, ensure_ascii=False)}\n")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
            
            if stream:
                reply = ""
                print("思考中:\n")
                try:
                    for chunk in response:
                        if not chunk.choices or len(chunk.choices) == 0:
                            continue
                        
                        # 有些chunk可能没有content，只有role等其他信息
                        delta = chunk.choices[0].delta
                        delta_content = getattr(delta, 'content', None)
                        
                        if delta_content is not None:
                            print(delta_content, end="", flush=True)
                            reply += delta_content
                except Exception as e:
                    print(f"\n流式输出处理错误: {str(e)}")
            else:
                if not response.choices:
                    return ""
                reply = response.choices[0].message.content
                
            end_time = time.time()
            print(f"\n调用耗时: {end_time - start_time:.2f}秒")
            return reply
            
        except Exception as e:
            print(f"API调用错误: {str(e)}")
            return ""

def qwen_qwq_call(system_prompt: str, user_input: str, history: List[Message] = None) -> str:
    invoker = OpenAIInvoker(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    return invoker.call(
        model="qwq-plus",
        system_prompt=system_prompt,
        user_input=user_input,
        history=history,
        stream=True,
    )

def deepseek_r1_call(system_prompt: str, user_input: str, history: List[Message] = None) -> str:
    invoker = OpenAIInvoker(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )
    return invoker.call(
        model="deepseek-reasoner", 
        system_prompt=system_prompt,
        user_input=user_input,
        history=history,
        stream=True
    )

