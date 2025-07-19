# 迁移到 uv 包管理器

本文档记录了项目从 `requirements.txt` 迁移到 `uv` 包管理器的过程。

## 迁移完成的内容

### 1. 安装 uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 项目配置文件
- ✅ 创建了 `pyproject.toml` 配置文件
- ✅ 生成了 `uv.lock` 锁定文件
- ✅ 设置了 `.python-version` 文件 (3.12.6)

### 3. 依赖管理
- ✅ 从 `requirements.txt` 导入所有依赖到 `pyproject.toml`
- ✅ 所有依赖版本已锁定在 `uv.lock` 中
- ✅ 依赖树验证通过 (95个包)

### 4. Docker 支持
- ✅ 更新 `Dockerfile` 使用 uv 进行依赖安装
- ✅ 优化了构建缓存和分层
- ✅ 更新了 `.dockerignore` 文件

### 5. 开发工具
- ✅ 创建了 `scripts/dev.sh` 开发脚本
- ✅ 更新了 `README.md` 文档

## 新的工作流程

### 日常开发命令
```bash
# 安装依赖
uv sync

# 运行应用
uv run python main.py

# 添加新依赖
uv add <package-name>

# 添加开发依赖
uv add --dev <package-name>

# 更新依赖
uv lock --upgrade

# 查看依赖树
uv tree
```

### 使用开发脚本
```bash
# 安装依赖
./scripts/dev.sh install

# 运行应用
./scripts/dev.sh run

# 添加依赖
./scripts/dev.sh add <package-name>

# 构建 Docker 镜像
./scripts/dev.sh build
```

## 迁移优势

1. **更快的依赖解析**: uv 比 pip 快 10-100 倍
2. **更好的依赖锁定**: `uv.lock` 提供完整的依赖图锁定
3. **统一的项目配置**: `pyproject.toml` 标准化项目元数据
4. **更好的缓存机制**: 全局缓存减少重复下载
5. **更可靠的构建**: 确定性的依赖解析

## 文件变更

### 新增文件
- `pyproject.toml` - 项目配置和依赖
- `uv.lock` - 依赖锁定文件
- `.python-version` - Python 版本指定
- `scripts/dev.sh` - 开发脚本
- `MIGRATION.md` - 本文档

### 修改文件
- `README.md` - 更新使用说明
- `Dockerfile` - 使用 uv 构建
- `.dockerignore` - 优化构建

### 保留文件
- `requirements.txt` - 保留作为备份，但不再使用

## 验证

项目迁移后已验证：
- ✅ 所有依赖正确安装
- ✅ 应用可以正常启动
- ✅ Docker 构建成功
- ✅ 开发脚本工作正常

## 后续步骤

1. 团队成员需要安装 uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. 使用 `uv sync` 替代 `pip install -r requirements.txt`
3. 可以考虑删除 `requirements.txt` 文件（已在 `.dockerignore` 中排除） 