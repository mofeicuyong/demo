# 1. 使用 Python 3.9 作为基础镜像
FROM python:3.9

# 2. 设置容器的工作目录为 /app
WORKDIR /app

# 3. 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 复制所有代码到 /app
COPY . .

# 5. 进入 Django 项目目录
WORKDIR /app/djangoProject

# 6. 运行 Django 服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
