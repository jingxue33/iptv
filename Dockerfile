# 使用官方Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建输出目录
RUN mkdir -p output/m3u output/txt

# 设置环境变量，用于指定配置文件路径
ENV CONFIG_PATH=/app/config/config.json

# 指定容器启动时执行的命令
CMD ["python", "scripts/main.py"]