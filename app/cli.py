import os
import time
from typing import Optional, Dict, Any
from dashscope.api_entities.dashscope_response import Message

from app import const
from app.llm import OpenAIInvoker
from app.prompt import system_prompts
from app.tool.sql import execute_sql_to_csv
from app.tool import extractor
from app.agent import store

class CLIChat:
    def __init__(self):
        self.current_provider = "4"  # 默认使用DeepSeek
        self.current_model = "deepseek-reasoner"  # 默认模型 DeepSeek-R1
        self.history: list[Message] = []
        self.system_prompt = ''
        self.session_id = ''
        self.csv_path = ''
        self.invoker = self._create_invoker()
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME')
        }

    def reset(self):
        self.history: list[Message] = []
        self.system_prompt = ""
        self.session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.csv_path = store.get_csv_path(self.session_id)

    def _create_invoker(self) -> OpenAIInvoker:
        self.reset()
        provider = const.PROVIDERS[self.current_provider]
        api_key = os.getenv(provider["env_key"])
        if not api_key:
            raise ValueError(f"未设置环境变量 {provider['env_key']}")
        return OpenAIInvoker(
            api_key=api_key,
            base_url=provider["base_url"]
        )

    def execute_sql(self, sql: str) -> str:
        try:
            results = execute_sql_to_csv(sql, self.csv_path, self.db_config)
            if results:
                print(f"\nSQL执行成功，结果已保存到: {self.csv_path}\n")
                print(f"SQL 语句: {sql}")
                return results
            else:
                print("\n未查到任何统计数据，请重新调整查询条件")
                return ''
        except Exception as e:
            print(f"\nSQL执行错误: {str(e)}")
            return ''

    def process_sql_query(self, user_input: str) -> tuple[str, str, str, int]:
        # 将时间字符串转换为时间戳进行比较
        session_time = time.mktime(time.strptime(self.session_id, "%Y%m%d%H%M%S"))
        if time.time() - session_time > 1800:  # 30分钟 = 1800秒
            self.session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
            self.csv_path = store.get_csv_path(self.session_id)
        system_prompt, history = store.prompt_prepare(
            user_input, self.system_prompt, self.session_id, self.history)

        if not history:
            user_input += f"""请结合领域知识和背景，生成 MySQL 8.0 直接运行的查询语句，并根据情况推荐适合的统计图表编号.\n
            数据库建表语句如下:\n {system_prompts.ddl_sql}\n
            """
        response = self.invoker.call(
            model=self.current_model,
            system_prompt=system_prompt,
            user_input=user_input,
            history=history,
            stream=True
        )
        sqls = extractor.extract_sql_queries(response)
        sql = ''
        char_type = 1
        results = ''
        if sqls:
            if len(sqls) > 1:
                print("\n检测到多个SQL语句，将执行第一个:")
                for i, _sql in enumerate(sqls, 1):
                    print(f"SQL {i}: {_sql}")
            sql = sqls[0]
            results = self.execute_sql(sql)
            if results:
                print("\n查询结果:")
                print(results)
        else:
            print("\nAI回复:")
            print(response)
        if "图表编号:" in response:
            # 提取图表编号，并转为数字。数字后面可能有其他字符，要避免和后面的非数字粘连
            char_type = int([c for c in response.split("图表编号:")[1].split(",")[0] if c.isdigit()][0])
        self.history.append(Message(role='user', content=user_input))
        self.history.append(Message(role='assistant', content=response))
        store.store_context(self.session_id, self.history)
        return response, sql, results, char_type

    def cli_switch_provider(self):
        print("\n可用的大模型提供商：")
        for key, provider in const.PROVIDERS.items():
            print(f"{key}. {provider['name']}({provider['models'][0]})")
        
        choice = input("请选择提供商 (1-4): ").strip()
        if choice in const.PROVIDERS:
            self.switch_provider(choice)
        else:
            print("无效的选择，保持当前设置")

    def switch_provider(self, choice):
        self.current_provider = choice
        self.current_model = const.PROVIDERS[choice]["models"][0]
        self.invoker = self._create_invoker()
        print(f"已切换到提供商 {const.PROVIDERS[choice]['name']}，默认模型：{self.current_model}")

    def switch_model(self, choice):
        self.current_model = choice
        self.reset()
        print(f"已切换到模型参数：{self.current_model}")

    def cli_switch_model(self):
        provider = const.PROVIDERS[self.current_provider]
        print(f"\n[{provider['name']}]当前可用的模型:")
        for i, model in enumerate(provider["models"], 1):
            print(f"{i}. {model}")
        
        choice = input("请选择模型参数: ").strip()
        try:
            if choice in const.PROVIDERS[self.current_provider]["models"]:
                self.switch_model(choice)
                return
            idx = int(choice) - 1
            if 0 <= idx < len(provider["models"]):
                self.switch_model(provider["models"][idx])
            else:
                print("无效的选择，保持当前设置")
        except ValueError:
            print("无效的输入，保持当前设置")

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
        print("系统提示词已更新")

    def clear_history(self):
        self.reset()
        print("对话历史已清除")

    def chat(self, user_input: str) -> str:
        print(f"----- {const.PROVIDERS[self.current_provider]['name']} streaming request with LLM {self.current_model} -----")
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
        for key, provider in const.PROVIDERS.items():
            print(f"{key}. {provider['name']}({provider['models'][0]})")
        
        choice = input("请选择提供商 (1-4): ").strip()
        if choice in const.PROVIDERS:
            self.switch_provider(choice)
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
            provider = const.PROVIDERS[self.current_provider]
            prompt = f"\n[{provider['name']}({self.current_model})]>"
            user_input = input(prompt).strip()

            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'clear':
                self.clear_history()
                continue
            elif user_input.lower() == 'switch':
                self.cli_switch_provider()
                continue
            elif user_input.lower() == 'model':
                self.cli_switch_model()
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

