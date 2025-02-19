# 1. 选择 Python 作为基础镜像
FROM python:3.9

# 2. 设置工作目录
WORKDIR /djangoProject

# 3. 复制 requirements.txt
COPY requirements.txt .

# 4. 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制所有项目代码
COPY . .

# 6. 运行应用
CMD ["python", "manage.py"]
