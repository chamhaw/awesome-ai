FROM python:3.12

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

USER root
RUN /usr/sbin/groupadd app \
    && /usr/sbin/useradd -g app app \
    && mkdir -p /app

WORKDIR /app

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 安装依赖 (使用uv)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 复制应用代码
COPY . .
RUN chown -R app:app /app

EXPOSE 5050

USER app
# 未支持手动传入端口号等参数
CMD ["uv", "run", "python", "main.py"]