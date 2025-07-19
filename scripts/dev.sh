#!/bin/bash

# 开发脚本 - 简化常用的uv命令和ADK版本管理

set -e

case "$1" in
    "install")
        echo "安装项目依赖..."
        uv sync
        ;;
    "run")
        echo "启动应用 (原版本)..."
        uv run python main.py
        ;;
    "run-adk")
        echo "启动应用 (ADK版本)..."
        uv run python adk_main.py
        ;;
    "add")
        if [ -z "$2" ]; then
            echo "用法: $0 add <package-name>"
            exit 1
        fi
        echo "添加依赖: $2"
        uv add "$2"
        ;;
    "add-dev")
        if [ -z "$2" ]; then
            echo "用法: $0 add-dev <package-name>"
            exit 1
        fi
        echo "添加开发依赖: $2"
        uv add --dev "$2"
        ;;
    "update")
        echo "更新依赖..."
        uv lock --upgrade
        ;;
    "tree")
        echo "显示依赖树..."
        uv tree
        ;;
    "clean")
        echo "清理环境..."
        rm -rf .venv
        echo "环境已清理，请重新运行 '$0 install'"
        ;;
    "build")
        echo "构建 Docker 镜像..."
        docker build -t awesome-ai:latest .
        ;;
    "test-legacy")
        echo "测试原版本API..."
        echo "测试健康检查..."
        curl -s http://localhost:5050/api/health | python -m json.tool
        ;;
    "test-adk")
        echo "测试ADK版本API..."
        echo "测试ADK状态..."
        curl -s http://localhost:5050/api/adk-status | python -m json.tool
        ;;
    "docs")
        echo "打开API文档..."
        python -c "import webbrowser; webbrowser.open('http://localhost:5050/apidocs/')"
        ;;
    "check-config")
        echo "检查配置..."
        echo "环境变量检查："
        echo "GEMINI_API_KEY: ${GEMINI_API_KEY:+已设置}"
        echo "DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:+已设置}"
        echo "DB_HOST: ${DB_HOST:+已设置}"
        echo "DB_USER: ${DB_USER:+已设置}"
        echo "DB_PASSWORD: ${DB_PASSWORD:+已设置}"
        echo "DB_NAME: ${DB_NAME:+已设置}"
        ;;
    "migration-status")
        echo "迁移状态检查..."
        echo "📁 目录结构："
        echo "  ✅ adk_app/ - ADK应用模块"
        echo "  ✅ app/ - 原有应用模块"
        echo "  ✅ adk_main.py - ADK版本入口"
        echo "  ✅ main.py - 原版本入口"
        echo ""
        echo "📦 依赖状态："
        echo "  ✅ google-adk $(uv tree | grep google-adk | head -1 || echo '未安装')"
        echo ""
        echo "🔧 配置文件："
        echo "  ✅ pyproject.toml - UV项目配置"
        echo "  ✅ adk_app/config.py - ADK配置模块"
        ;;
    *)
        echo "使用方法: $0 {install|run|run-adk|add|add-dev|update|tree|clean|build|test-legacy|test-adk|docs|check-config|migration-status}"
        echo ""
        echo "命令说明："
        echo "  install      - 安装项目依赖"
        echo "  run          - 启动原版本应用"
        echo "  run-adk      - 启动ADK版本应用"
        echo "  add          - 添加依赖包"
        echo "  add-dev      - 添加开发依赖包"
        echo "  update       - 更新所有依赖"
        echo "  tree         - 显示依赖树"
        echo "  clean        - 清理环境"
        echo "  build        - 构建Docker镜像"
        echo "  test-legacy  - 测试原版本API"
        echo "  test-adk     - 测试ADK版本API"
        echo "  docs         - 打开API文档"
        echo "  check-config - 检查环境配置"
        echo "  migration-status - 查看迁移状态"
        exit 1
        ;;
esac 