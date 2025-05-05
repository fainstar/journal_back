"""
共用模組，提供全局設定、資料庫連接和日誌功能
"""
import os
import sqlite3
import logging
from pathlib import Path

# 設置日誌，使用 UTF-8 編碼支援中文
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'  # 添加 UTF-8 編碼設定
)
logger = logging.getLogger(__name__)

# 設定類
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

# 建立資料庫連接工廠函數
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