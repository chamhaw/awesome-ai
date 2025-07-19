#!/usr/bin/env python3
"""
Awesome AI - ADK版本主入口
基于Google ADK 1.1.1的智能BI数据分析应用
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from chat_bi.server import run_server
from chat_bi.config import app_config


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Awesome AI - ADK版本启动中...")
    print("基于Google ADK 1.1.1的智能BI数据分析应用")
    print("=" * 60)
    
    # 配置验证
    if not app_config.validate():
        print("❌ 配置验证失败，请检查以下环境变量：")
        if not app_config.database.host:
            print("  - DB_HOST")
        if not app_config.database.user:
            print("  - DB_USER")
        print("\n请设置必要的环境变量后重新启动应用。")
        return 1
    
    print("✅ 配置验证通过")
    print(f"📊 数据库: {app_config.database.host}")
    print(f"🤖 模型: {app_config.llm.default_model}")
    print(f"🌐 服务地址: {app_config.server.server_url}")
    print(f"📚 API文档: {app_config.server.server_url}/apidocs/")
    print("")
    
    # 启动服务器
    try:
        run_server()
        return None
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
        return 0
    except Exception as e:
        print(f"\n❌ 应用启动失败: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 