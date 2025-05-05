FROM python:3.10-slim

WORKDIR /app

# 複製依賴文件
COPY requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 創建上傳目錄
RUN mkdir -p /app/uploads/images

# 暴露 FastAPI 默認端口
EXPOSE 8000

# 啟動應用
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]