from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sqlite3
from pathlib import Path
import logging
from typing import List, Dict
import importlib

# 設置日誌
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="日記本 API",
    description="一個支援圖片上傳和 Markdown 格式的日記本系統",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立config模組 - 方便未來配置管理
class Config:
    UPLOAD_FOLDER = "uploads/images"
    DB_PATH = "diary.db"
    API_VERSION = "1.0.0"
    
    # 未來可擴充設定項
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    @classmethod
    def init(cls):
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)

# 初始化設定
Config.init()

# 建立資料庫連接工廠函數 - 方便未來切換資料庫
def get_db_connection():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row  # 使結果以字典形式返回
    return conn

# 建立資料表
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # 建立圖片表
        cursor.execute('''CREATE TABLE IF NOT EXISTS images
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # 建立文章表
        cursor.execute('''CREATE TABLE IF NOT EXISTS markdown_notes
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # 未來可擴充的標籤表
        cursor.execute('''CREATE TABLE IF NOT EXISTS tags
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # 文章-標籤關聯表
        cursor.execute('''CREATE TABLE IF NOT EXISTS note_tags
                        (note_id INTEGER,
                        tag_id INTEGER,
                        PRIMARY KEY (note_id, tag_id),
                        FOREIGN KEY (note_id) REFERENCES markdown_notes(id) ON DELETE CASCADE,
                        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE)''')
        
        conn.commit()

# 初始化資料庫
init_db()

@app.post("/upload-image/", tags=["圖片管理"])
async def upload_image(file: UploadFile = File(...)):
    """
    上傳圖片檔案
    
    - **file**: 要上傳的圖片檔案（支援常見圖片格式）
    
    Returns:
        - **url**: 上傳後的圖片 URL
    """
    try:
        # 計算檔案hash值
        file_content = await file.read()
        import hashlib
        file_hash = hashlib.md5(file_content).hexdigest()
        file_extension = Path(file.filename).suffix
        
        # 儲存圖片
        file_location = Path(Config.UPLOAD_FOLDER) / f"{file_hash}{file_extension}"
        with open(file_location, "wb") as f:
            f.write(file_content)
        
        # 儲存圖片URL到數據庫
        image_url = f"http://127.0.0.1:8000/get-image/{file_hash}{file_extension}"
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO images (url, filename) VALUES (?, ?)", (image_url, f"{file_hash}{file_extension}"))
            conn.commit()
        
        # 回傳圖片 URL
        logger.info(f"成功上傳圖片: {file_hash}{file_extension}")
        return JSONResponse(content={"url": image_url})
    except Exception as e:
        logger.error(f"上傳圖片失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-markdown/", tags=["文章管理"])
async def save_markdown(data: dict):
    """
    保存 Markdown 格式的文章
    
    - **content**: Base64 編碼的 Markdown 內容
    
    Returns:
        - **message**: 成功訊息
        - **note_id**: 文章 ID
        - **content_length**: 內容長度
    """
    try:
        # 解碼base64內容
        import base64
        content = base64.b64decode(data["content"]).decode('utf-8')
        
        # 連接SQLite資料庫
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO markdown_notes (content) VALUES (?)", (content,))
            conn.commit()
            last_id = cursor.lastrowid
        
        logger.info(f"成功保存文章，ID: {last_id}")
        return {"message": "Markdown saved to database successfully!", "note_id": last_id, "content_length": len(content)}
    except Exception as e:
        logger.error(f"保存文章失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-upload-image/")
async def test_upload_image():
    """
    测试图片上传接口
    返回示例请求体和说明
    """
    return {
        "description": "测试图片上传接口",
        "example_request": {
            "method": "POST",
            "url": "/upload-image/",
            "headers": {"Content-Type": "multipart/form-data"},
            "body": {"file": "(binary image data)"}
        },
        "expected_response": {
            "url": "/uploads/images/filename.jpg"
        }
    }

@app.get("/get-image/{filename}")
async def get_image(filename: str):
    """
    获取上传的图片
    """
    file_location = Path(Config.UPLOAD_FOLDER) / filename
    if not file_location.exists():
        return JSONResponse(
            status_code=404,
            content={"message": "Image not found"}
        )
    return FileResponse(str(file_location))

@app.get("/test-save-markdown/")
async def test_save_markdown():
    """
    测试Markdown保存接口
    返回示例请求体和说明
    """
    return {
        "description": "测试Markdown保存接口",
        "example_request": {
            "method": "POST",
            "url": "/save-markdown/",
            "headers": {"Content-Type": "application/json"},
            "body": {"content": "# 这是一个Markdown示例"}
        },
        "expected_response": {
            "message": "Markdown saved to database successfully!",
            "note_id": 1,
            "content_length": 15
        }
    }

@app.get("/get-all-images/", tags=["圖片管理"])
async def get_all_images():
    """
    獲取所有已上傳的圖片列表
    
    Returns:
        - **images**: 圖片列表，包含 URL 和檔名
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url, filename FROM images ORDER BY created_at DESC")
            images = cursor.fetchall()
        logger.info("成功獲取所有圖片列表")
        return {"images": images}
    except Exception as e:
        logger.error(f"獲取圖片列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-all-notes/", tags=["文章管理"])
async def get_all_notes():
    """
    獲取所有已保存的文章列表
    
    Returns:
        - **notes**: 文章列表，包含 ID、內容和建立時間
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content, created_at FROM markdown_notes ORDER BY created_at DESC")
            notes = cursor.fetchall()
        logger.info("成功獲取所有文章列表")
        return {"notes": notes}
    except Exception as e:
        logger.error(f"獲取文章列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=FileResponse)
async def serve_html():
    """
    返回前端HTML界面
    """
    return FileResponse("index.html")

@app.delete("/delete-image/{filename}")
async def delete_image(filename: str):
    """
    刪除指定圖片
    """
    file_location = Path(Config.UPLOAD_FOLDER) / filename
    if not file_location.exists():
        return JSONResponse(
            status_code=404,
            content={"message": "Image not found"}
        )
    
    # 從數據庫刪除記錄
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM images WHERE filename = ?", (filename,))
        conn.commit()
    
    # 刪除文件
    os.remove(file_location)
    return {"message": "Image deleted successfully"}

@app.put("/update-note/{note_id}")
async def update_note(note_id: int, data: dict):
    """
    更新指定文章
    """
    import base64
    content = base64.b64decode(data["content"]).decode('utf-8')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE markdown_notes SET content = ? WHERE id = ?", (content, note_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return JSONResponse(
                status_code=404,
                content={"message": "Note not found"}
            )
    
    return {"message": "Note updated successfully"}

@app.delete("/delete-note/{note_id}")
async def delete_note(note_id: int):
    """
    刪除指定文章
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM markdown_notes WHERE id = ?", (note_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return JSONResponse(
                status_code=404,
                content={"message": "Note not found"}
            )
    
    return {"message": "Note deleted successfully"}

@app.get("/get-note/{note_id}")
async def get_note(note_id: int):
    """
    獲取指定文章
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, content, created_at FROM markdown_notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        
        if not note:
            return JSONResponse(
                status_code=404,
                content={"message": "Note not found"}
            )
    
    return {"note": note}

@app.get("/get-image-info/{filename}")
async def get_image_info(filename: str):
    """
    獲取指定圖片信息
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url, filename, created_at FROM images WHERE filename = ?", (filename,))
        image = cursor.fetchone()
        
        if not image:
            return JSONResponse(
                status_code=404,
                content={"message": "Image not found"}
            )
    
    return {"image": image}

