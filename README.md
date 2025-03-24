# AI 生成 SQL 并执行输出 CSV 文件

## 部署
### 镜像构建
在项目根目录下执行以下命令
`docker build -t ai-sql-csv:latest .`
### 容器运行
准备以下关键环境变量
```yaml
DASHSCOPE_LLAMA_INDEX_NAME # 必填，阿里云 DashScope LLM 索引名称，用于远程知识库
DASHSCOPE_API_KEY # 必填，阿里云 DashScope API Key
DEEPSEEK_API_KEY # 必填，DeepSeek API Key，使用了 DeepSeek官方版 R1

DB_HOST
DB_NAME
DB_USER
DB_PASSWORD

SERVER_URL # 非必须，默认是 http://localhost:5050
```
运行容器
`docker run -d --name ai-sql-csv -p 5000:5000 -e DASHSCOPE_LLAMA_INDEX_NAME=<your-index-name> -e DASHSCOPE_API_KEY=<your-api-key> -e DEEPSEEK_API_KEY=<your-deepseek-api-key> -e DB_HOST=<your-db-host> -e DB_NAME=<your-db-name> -e DB_USER=<your-db-user> -e DB_PASSWORD=<your-db-password> ai-sql-csv:latest`
## 本地开发
### 设置环境变量
如果清楚如何在运行时环境变量中设置容器运行的关键环境变量，可以跳过此步骤。
否则推荐使用 .env文件设置环境变量。
1. 在项目根目录创建 .env 文件
    ```bash
    DASHSCOPE_LLAMA_INDEX_NAME=<your-index-name>
    DASHSCOPE_API_KEY=<your-api-key>
    DEEPSEEK_API_KEY=<your-deepseek-api-key>
    DB_HOST=<your-db-host>
    DB_NAME=<your-db-name>
    DB_USER=<your-db-user>
    DB_PASSWORD=<your-db-password>
    SERVER_URL=http://localhost:5050 # 非必须, 默认是 http://localhost:5050, 用于后端拼接 csv 下载链接
    ```
2. 启动应用
   在项目根目录下运行 `python main.py`

