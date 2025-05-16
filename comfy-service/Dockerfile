# FROM python:3.11 
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装Python依赖
# 安装 distutils（修复 ModuleNotFoundError）
# RUN apt-get update && apt-get install -y python3-distutils
RUN pip3 install --no-cache-dir -r requirements.txt

# 设置Python路径
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8101

# 启动服务
CMD ["python3", "main.py"] 