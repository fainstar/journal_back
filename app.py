from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import os

# 導入模組化路由
from routers import images, notes, tags
from common import Config, init_db, logger

# 建立主應用程式
app = FastAPI(
    title="日記本 API",
    description="一個支援圖片上傳和 Markdown 格式的日記本系統",
    version=Config.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 初始化資料庫
init_db()

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立靜態文件目錄
os.makedirs("static", exist_ok=True)

# 設置模板引擎 - 將模板目錄更新為 static/templates
templates = Jinja2Templates(directory="static/templates")

# 掛載靜態文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 整合路由模組
app.include_router(images.router)
app.include_router(notes.router)
app.include_router(tags.router)

# 根路由導向前端
@app.get("/", response_class=HTMLResponse)
async def serve_html(request: Request):
    """
    返回前端HTML界面
    """
    return templates.TemplateResponse("index.html", {"request": request})

# 健康檢查
@app.get("/health")
async def health_check():
    """
    系統健康檢查
    """
    return {
        "status": "ok",
        "version": Config.API_VERSION
    }

# 啟動指令
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )