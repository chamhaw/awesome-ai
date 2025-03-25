from dotenv import load_dotenv
from app.cli import CLIChat

if __name__ == "__main__":
    # 加载 .env 文件
    load_dotenv()
    chat = CLIChat()
    chat.run() 