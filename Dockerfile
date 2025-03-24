FROM python:3.12
USER root
RUN /usr/sbin/groupadd app \
    && /usr/sbin/useradd -g app app \
    && mkdir -p /app
ADD . /app
WORKDIR /app
RUN chown -R app:app /app && pip install -r requirements.txt

EXPOSE 5050

USER app
# 未支持手动传入端口号等参数
CMD ["python", "main.py"]