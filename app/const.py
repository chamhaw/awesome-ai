PROVIDERS = {
    "1": {"name": "ChatGPT", "base_url": "https://api.openai.com/v1", "env_key": "OPENAI_API_KEY",
          "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]},
    "2": {"name": "Qwen", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
          "env_key": "DASHSCOPE_API_KEY", "models": ["deepseek-reasoner", "deepseek-chat","qwen-max", "qwen-turbo", "qwen-plus", "qwq-plus"]},
    "3": {"name": "Ark", "base_url": "https://ark.cn-beijing.volces.com/api/v1", "env_key": "ARK_API_KEY",
          "models": ["doubao-pro-32k"]},
    "4": {"name": "DeepSeek", "base_url": "https://api.deepseek.com", "env_key": "DEEPSEEK_API_KEY",
          "models": ["deepseek-reasoner", "deepseek-chat", "deepseek-coder"]}
}
