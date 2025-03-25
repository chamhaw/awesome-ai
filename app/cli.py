import os
import time
from typing import Optional, Dict, Any
from dashscope.api_entities.dashscope_response import Message
from app.llm import OpenAIInvoker
from app.tool.sql import execute_sql_to_csv
from app.tool import extractor
from app.agent import store

class CLIChat:
    def __init__(self):
        self.providers = {
            "1": {"name": "ChatGPT", "base_url": "https://api.openai.com/v1", "env_key": "OPENAI_API_KEY", "models": ["gpt-4o","gpt-4o-mini", "gpt-4-turbo"]},
            "2": {"name": "Qwen", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "env_key": "DASHSCOPE_API_KEY", "models": ["qwen-turbo", "qwen-plus", "qwen-max", "qwq-plus"]},
            "3": {"name": "Ark", "base_url": "https://ark.cn-beijing.volces.com/api/v1", "env_key": "ARK_API_KEY", "models": ["doubao-pro-32k"]},
            "4": {"name": "DeepSeek", "base_url": "https://api.deepseek.com", "env_key": "DEEPSEEK_API_KEY", "models": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"]}
        }
        self.current_provider = "2"  # 默认使用Qwen
        self.current_model = "qwen-max"  # 默认模型
        self.history: list[Message] = []
        self.system_prompt = ""
        self.invoker = self._create_invoker()
        self.session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.csv_path = store.get_csv_path(self.session_id)
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME')
        }

    def _create_invoker(self) -> OpenAIInvoker:
        provider = self.providers[self.current_provider]
        api_key = os.getenv(provider["env_key"])
        if not api_key:
            raise ValueError(f"未设置环境变量 {provider['env_key']}")
        return OpenAIInvoker(
            api_key=api_key,
            base_url=provider["base_url"]
        )

    def execute_sql(self, sql: str) -> Optional[str]:
        try:
            results = execute_sql_to_csv(sql, self.csv_path, self.db_config)
            if results:
                print(f"\nSQL执行成功，结果已保存到: {self.csv_path}\n")
                print(f"SQL 语句: {sql}")
                return results
            else:
                print("\n未查到任何统计数据，请重新调整查询条件")
                return None
        except Exception as e:
            print(f"\nSQL执行错误: {str(e)}")
            return None

    def process_sql_query(self, user_input: str):
        # 将时间字符串转换为时间戳进行比较
        session_time = time.mktime(time.strptime(self.session_id, "%Y%m%d%H%M%S"))
        if time.time() - session_time > 1800:  # 30分钟 = 1800秒
            self.session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        system_prompt, user_prompt, history = store.prompt_prepare(
            user_input, self.system_prompt, self.session_id, self.history)
        
        response = self.invoker.call(
            model=self.current_model,
            system_prompt=system_prompt,
            user_input=user_prompt,
            history=history,
            stream=True
        )
        
        sqls = extractor.extract_sql_queries(response)
        if sqls:
            if len(sqls) > 1:
                print("\n检测到多个SQL语句，将执行第一个:")
                for i, sql in enumerate(sqls, 1):
                    print(f"SQL {i}: {sql}")
            
            results = self.execute_sql(sqls[0])
            if results:
                print("\n查询结果:")
                print(results)
        else:
            print("\nAI回复:")
            print(response)
        
        self.history.append(Message(role='user', content=user_input))
        self.history.append(Message(role='assistant', content=response))
        store.store_context(self.session_id, self.history)

    def switch_provider(self):
        print("\n可用的大模型提供商：")
        for key, provider in self.providers.items():
            print(f"{key}. {provider['name']}({provider['models'][0]})")
        
        choice = input("请选择提供商 (1-4): ").strip()
        if choice in self.providers:
            self.current_provider = choice
            self.current_model = self.providers[choice]["models"][0]
            self.invoker = self._create_invoker()
            self.clear_history()
            print(f"已切换到提供商 {self.providers[choice]['name']}，默认模型：{self.current_model}")
        else:
            print("无效的选择，保持当前设置")

    def switch_model(self):
        provider = self.providers[self.current_provider]
        print(f"\n[{provider['name']}]当前可用的模型:")
        for i, model in enumerate(provider["models"], 1):
            print(f"{i}. {model}")
        
        choice = input("请选择模型参数: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(provider["models"]):
                self.current_model = provider["models"][idx]
                self.clear_history()
                print(f"已切换到模型参数：{self.current_model}")
            else:
                print("无效的选择，保持当前设置")
        except ValueError:
            print("无效的输入，保持当前设置")

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
        print("系统提示词已更新")

    def clear_history(self):
        self.history = []
        self.session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        print("对话历史已清除")

    def chat(self, user_input: str) -> str:
        print(f"----- {self.providers[self.current_provider]['name']} streaming request with LLM {self.current_model} -----")
        response = self.invoker.call(
            model=self.current_model,
            system_prompt=self.system_prompt,
            user_input=user_input,
            history=self.history,
            stream=True
        )
        self.history.append(Message(role='user', content=user_input))
        self.history.append(Message(role='assistant', content=response))
        return response

    def run(self):
        print("欢迎使用 AI 助手！\n")
        print("可用的大模型提供商：")
        for key, provider in self.providers.items():
            print(f"{key}. {provider['name']}({provider['models'][0]})")
        
        choice = input("请选择提供商 (1-4): ").strip()
        if choice in self.providers:
            self.current_provider = choice
            self.current_model = self.providers[choice]["models"][0]
            self.invoker = self._create_invoker()
            print(f"已切换到提供商 {self.providers[choice]['name']}，默认模型：{self.current_model}")
        else:
            print("无效的选择，使用默认设置")

        print("\n初始化完成！现在可以开始对话了。")
        print("输入 'exit' 退出程序")
        print("输入 'clear' 清除历史")
        print("输入 'switch' 切换模型")
        print("输入 'model' 切换模型参数")
        print("输入 'system: <提示词>' 设置系统提示词")
        print("输入 'sql: <SQL语句>' 执行SQL查询")
        print("-" * 40)

        while True:
            provider = self.providers[self.current_provider]
            prompt = f"\n[{provider['name']}({self.current_model})]>"
            user_input = input(prompt).strip()

            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'clear':
                self.clear_history()
                continue
            elif user_input.lower() == 'switch':
                self.switch_provider()
                continue
            elif user_input.lower() == 'model':
                self.switch_model()
                continue
            elif user_input.lower().startswith('system:'):
                self.set_system_prompt(user_input[7:].strip())
                continue
            elif user_input.lower().startswith('sql:'):
                sql = user_input[4:].strip()
                self.execute_sql(sql)
                continue

            if user_input:
                self.process_sql_query(user_input) 