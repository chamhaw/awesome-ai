# Awesome AI - Google ADK 1.1.1 重构指南

本文档介绍了基于Google ADK 1.1.1的应用重构情况和使用方法。

## 🚀 重构概述

### 架构设计

我们基于现代开源agent应用的最佳实践，设计了新的目录结构：

```
awesome-ai/
├── adk_app/                    # 新的ADK应用模块
│   ├── __init__.py            # 包初始化
│   ├── config.py              # 统一配置管理
│   ├── agents.py              # ADK智能代理
│   ├── tools.py               # ADK工具集
│   └── server.py              # Flask服务器
├── app/                       # 原有应用模块 (保持兼容)
├── adk_main.py                # ADK版本入口
├── main.py                    # 原版本入口 (保持兼容)
└── scripts/dev.sh             # 增强的开发脚本
```

### 核心特性

1. **🔄 完全向后兼容** - 保持原有API接口不变
2. **🤖 多代理架构** - BIAgent、SQLAgent、AnalysisAgent
3. **🛠️ 强化工具集** - SQL执行、图表推荐、数据验证
4. **⚙️ 统一配置** - 环境变量集中管理
5. **📊 增强API** - 新增ADK专用API端点

## 📦 安装和配置

### 1. 环境要求

- Python 3.12+
- Google ADK 1.1.1
- uv 包管理器

### 2. 安装依赖

```bash
# 安装所有依赖
./scripts/dev.sh install

# 或使用uv直接安装
uv sync
```

### 3. 环境配置

创建 `.env` 文件或设置环境变量：

```bash
# 必需的API密钥 (至少设置一个)
GEMINI_API_KEY=your_gemini_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# 数据库配置
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
DB_PORT=3306

# 服务器配置 (可选)
SERVER_HOST=0.0.0.0
SERVER_PORT=5050
DEBUG=false
SERVER_URL=http://localhost:5050
```

### 4. 配置检查

```bash
# 检查配置状态
./scripts/dev.sh check-config

# 查看迁移状态
./scripts/dev.sh migration-status
```

## 🚀 启动应用

### ADK版本 (推荐)

```bash
# 使用开发脚本启动
./scripts/dev.sh run-adk

# 或直接启动
uv run python adk_main.py
```

### 原版本 (兼容模式)

```bash
# 使用开发脚本启动
./scripts/dev.sh run

# 或直接启动
uv run python main.py
```

## 🔌 API接口

### 原有接口 (完全兼容)

- `POST /api/chat` - 生成SQL语句
- `POST /api/execute_sql` - 执行SQL查询
- `GET /api/download_file` - 下载CSV文件
- `GET /api/health` - 健康检查

### 新增ADK接口

- `POST /api/adk-chat` - ADK智能聊天 (支持多代理)
- `POST /api/adk-analysis` - ADK数据分析建议
- `GET /api/adk-status` - ADK代理状态

### API文档

启动应用后访问: http://localhost:5050/apidocs/

## 🤖 ADK代理系统

### 1. BIAgent (主要代理)

```python
from chat_bi.agents import BIAgent

agent = BIAgent()
response, sql, csv_results, chart_type, csv_path = agent.process_query(
   "查询销售数据趋势",
   session_id="20240101120000"
)
```

**功能特性:**
- 自然语言理解
- SQL生成和执行
- 图表推荐
- 数据质量验证
- 业务洞察分析

### 2. SQLAgent (SQL专家)

```python
from chat_bi.agents import SQLAgent

sql_agent = SQLAgent()
sql_result = sql_agent.generate_sql("查询用户订单信息")
```

**功能特性:**
- 专业SQL生成
- 查询优化建议
- 安全性验证
- 性能分析

### 3. AnalysisAgent (分析专家)

```python
from chat_bi.agents import AnalysisAgent

analysis_agent = AnalysisAgent()
analysis_result = analysis_agent.analyze_data(csv_data, "销售趋势分析")
```

**功能特性:**
- 数据质量评估
- 统计分析
- 图表推荐
- 业务洞察

## 🛠️ 工具集

### SQLExecutor
- 安全的SQL执行
- 结果CSV导出
- 错误处理

### ChartRecommender
- 智能图表推荐
- 9种图表类型支持
- 备选方案建议

### DataValidator
- 数据质量检查
- 清理建议
- 统计信息

## 📊 使用示例

### 1. 基本查询 (兼容原有API)

```bash
curl -X POST http://localhost:5050/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "查询销售数据",
    "provider": "2",
    "model": "deepseek-reasoner"
  }'
```

### 2. ADK智能查询

```bash
curl -X POST http://localhost:5050/api/adk-chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "分析最近3个月的销售趋势",
    "agent_type": "bi"
  }'
```

### 3. 专门的SQL生成

```bash
curl -X POST http://localhost:5050/api/adk-chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "优化用户订单查询",
    "agent_type": "sql"
  }'
```

### 4. 数据分析建议

```bash
curl -X POST http://localhost:5050/api/adk-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "query": "销售趋势分析",
    "data_result": "月份,销售额\n1月,100000\n2月,120000"
  }'
```

## 🔧 开发工具

### 开发脚本

```bash
# 基本操作
./scripts/dev.sh install          # 安装依赖
./scripts/dev.sh run              # 启动原版本
./scripts/dev.sh run-adk          # 启动ADK版本

# 依赖管理
./scripts/dev.sh add <package>    # 添加依赖
./scripts/dev.sh update           # 更新依赖
./scripts/dev.sh tree             # 查看依赖树

# 测试和调试
./scripts/dev.sh test-legacy      # 测试原版本API
./scripts/dev.sh test-adk         # 测试ADK版本API
./scripts/dev.sh docs             # 打开API文档

# 系统检查
./scripts/dev.sh check-config     # 检查配置
./scripts/dev.sh migration-status # 查看迁移状态
```

## 🐳 Docker部署

### 构建镜像

```bash
./scripts/dev.sh build
```

### 运行容器

```bash
docker run -d --name awesome-ai \
  -p 5050:5050 \
  -e GEMINI_API_KEY=your_key \
  -e DB_HOST=your_host \
  -e DB_USER=your_user \
  -e DB_PASSWORD=your_password \
  -e DB_NAME=your_database \
  awesome-ai:latest
```

## 🔍 监控和调试

### 健康检查

```bash
# 原版本健康检查
curl http://localhost:5050/api/health

# ADK代理状态
curl http://localhost:5050/api/adk-status
```

### 日志查看

```bash
# 查看应用日志
uv run python adk_main.py

# Docker日志
docker logs awesome-ai
```

## 🚧 迁移计划

### 阶段1: 基础架构 ✅
- [x] 创建ADK应用模块结构
- [x] 实现配置管理系统
- [x] 建立代理和工具框架
- [x] 保持API兼容性

### 阶段2: 核心功能
- [ ] 完善ADK代理实现
- [ ] 增强SQL生成能力
- [ ] 优化数据分析功能
- [ ] 添加更多工具

### 阶段3: 高级特性
- [ ] 多模型支持
- [ ] 流式响应
- [ ] 缓存机制
- [ ] 性能优化

## 📝 注意事项

1. **兼容性**: 原有API完全兼容，无需修改现有客户端
2. **配置**: 确保设置正确的API密钥和数据库连接
3. **性能**: ADK版本可能在首次启动时较慢，后续会优化
4. **错误处理**: 详细的错误信息会在API响应中返回

## 🆘 故障排除

### 常见问题

1. **ADK代理初始化失败**
   - 检查GEMINI_API_KEY是否设置
   - 确认网络连接正常

2. **数据库连接失败**
   - 验证数据库配置
   - 检查网络连通性

3. **依赖安装问题**
   - 使用 `./scripts/dev.sh clean` 清理环境
   - 重新运行 `./scripts/dev.sh install`

### 获取帮助

- 查看API文档: http://localhost:5050/apidocs/
- 检查系统状态: `./scripts/dev.sh migration-status`
- 查看配置: `./scripts/dev.sh check-config`

---

🎉 **恭喜！你已经成功将应用迁移到Google ADK 1.1.1架构。**

现在你可以享受更强大的AI功能和更好的代码组织结构！ 