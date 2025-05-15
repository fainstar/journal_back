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
    UPLOAD_FOLDER = "uploads/files"  # 統一的上傳資料夾
    DB_PATH = "diary.db"
    API_VERSION = "1.0.0"
    
    # 合併的檔案類型設定
    ALLOWED_EXTENSIONS = {
        'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        'video': {'mp4', 'webm', 'ogg'},
        'audio': {'mp3', 'wav'},
        'document': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'},
        'archive': {'zip', '7z', 'rar'}
    }
    
    # 檔案大小限制
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    @classmethod
    def init(cls):
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
    
    @classmethod
    def get_file_type(cls, extension: str) -> str:
        """根據副檔名判斷檔案類型"""
        extension = extension.lower()
        for file_type, extensions in cls.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                return file_type
        return "other"
    
    @classmethod
    def is_allowed_file(cls, filename: str) -> bool:
        """檢查檔案是否允許上傳"""
        extension = filename.split('.')[-1].lower()
        return any(extension in exts for exts in cls.ALLOWED_EXTENSIONS.values())

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
        
        # 建立檔案表
        cursor.execute('''CREATE TABLE IF NOT EXISTS files
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        original_filename TEXT NOT NULL,
                        size INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # 建立文章表
        cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # 建立標籤表
        cursor.execute('''CREATE TABLE IF NOT EXISTS tags
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # 建立文章標籤關聯表
        cursor.execute('''CREATE TABLE IF NOT EXISTS note_tags
                        (note_id INTEGER,
                        tag_id INTEGER,
                        FOREIGN KEY (note_id) REFERENCES notes (id),
                        FOREIGN KEY (tag_id) REFERENCES tags (id),
                        PRIMARY KEY (note_id, tag_id))''')
        
        # 建立檔案分享表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                share_code TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        """)
        
        # 移轉舊的圖片資料到新的檔案表
        try:
            cursor.execute("SELECT url, filename FROM images")
            old_images = cursor.fetchall()
            
            for image in old_images:
                # 檢查檔案是否已存在於新表中
                cursor.execute("SELECT id FROM files WHERE filename = ?", (image['filename'],))
                if not cursor.fetchone():
                    # 獲取檔案大小
                    file_path = os.path.join(Config.UPLOAD_FOLDER, image['filename'])
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    
                    # 插入到新表中
                    cursor.execute(
                        "INSERT INTO files (url, filename, original_filename, size, type) VALUES (?, ?, ?, ?, ?)",
                        (image['url'], image['filename'], image['filename'], file_size, 'image')
                    )
            
            # 刪除舊的圖片表
            cursor.execute("DROP TABLE IF EXISTS images")
            
        except Exception as e:
            logger.error(f"移轉圖片資料時發生錯誤: {str(e)}")
        
        conn.commit()
        
# 初始化資料庫
init_db()