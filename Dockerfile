FROM python:3.12
USER root
RUN /usr/sbin/groupadd app \
    && /usr/sbin/useradd -g app app \
    && mkdir -p /app \
    && chown -R app:app /app
USER app
ADD . /app

WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 5050
# 未支持手动传入端口号等参数
CMD ["python", "main.py"]