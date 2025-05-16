FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 设置环境变量
# ENV PYTHONPATH=/app
# ENV REDIS_HOST=redis
# ENV REDIS_PORT=6379
# ENV REDIS_PASSWORD=fuck
# ENV REDIS_DB=0

# 暴露端口
EXPOSE 7997

# 启动服务
CMD ["python3", "main.py"] 