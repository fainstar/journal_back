from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import hashlib
import os
from pathlib import Path
import sys
from typing import List

# 從common模組導入相關功能
from common import get_db_connection, Config, logger

router = APIRouter(
    prefix="/files",
    tags=["檔案管理"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    上傳檔案（支援圖片、影片、音訊等多種格式）
    
    - **file**: 要上傳的檔案
    
    Returns:
        - **url**: 上傳後的檔案 URL
        - **filename**: 檔案名稱
        - **originalFilename**: 原始檔名
        - **fileSize**: 檔案大小 (bytes)
        - **fileType**: 檔案類型 (image/video/audio/document/archive)
    """
    try:
        logger.info(f"開始處理檔案上傳: {file.filename}")
        
        # 驗證檔案類型
        file_extension = Path(file.filename).suffix.lower()[1:]
        logger.info(f"檔案副檔名: {file_extension}")
        
        if not Config.is_allowed_file(file.filename):
            logger.warning(f"不支援的檔案類型: {file_extension}")
            raise HTTPException(status_code=400, detail=f"不支援的檔案類型: {file_extension}")
            
        # 計算檔案hash值
        file_content = await file.read()
        file_size = len(file_content)
        file_hash = hashlib.md5(file_content).hexdigest()
        original_filename = file.filename
        stored_filename = f"{file_hash}{Path(file.filename).suffix}"
        
        logger.info(f"檔案資訊: 大小={file_size}bytes, Hash={file_hash}")
        
        # 儲存檔案
        file_location = Path(Config.UPLOAD_FOLDER) / stored_filename
        logger.info(f"儲存檔案位置: {file_location}")
        
        with open(file_location, "wb") as f:
            f.write(file_content)
        
        # 確定檔案類型
        file_type = Config.get_file_type(file_extension)
        logger.info(f"判斷檔案類型: {file_type}")
        
        # 構建檔案 URL
        file_url = f"http://127.0.0.1:8000/files/download/{stored_filename}"
        
        # 儲存檔案資訊到數據庫
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            logger.info("確保資料表存在")
            # 確保資料表存在
            cursor.execute('''CREATE TABLE IF NOT EXISTS files
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            url TEXT NOT NULL,
                            filename TEXT NOT NULL,
                            original_filename TEXT NOT NULL,
                            size INTEGER NOT NULL,
                            type TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            logger.info("插入檔案記錄到資料庫")
            cursor.execute(
                "INSERT INTO files (url, filename, original_filename, size, type) VALUES (?, ?, ?, ?, ?)",
                (file_url, stored_filename, original_filename, file_size, file_type)
            )
            conn.commit()
        
        logger.info(f"檔案上傳完成: {stored_filename}")
        return {
            "url": file_url,
            "filename": stored_filename,
            "originalFilename": original_filename,
            "fileSize": file_size,
            "fileType": file_type
        }
    except Exception as e:
        logger.error(f"上傳檔案失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    下載或預覽檔案
    
    - **filename**: 要下載的檔案名稱 (hash + 副檔名)
    """
    logger.info(f"請求下載/預覽檔案: {filename}")
    
    file_location = Path(Config.UPLOAD_FOLDER) / filename
    if not file_location.exists():
        logger.warning(f"請求的檔案不存在: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    
    # 從資料庫獲取原始檔名
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT original_filename, type FROM files WHERE filename = ?", (filename,))
        result = cursor.fetchone()
        
        if result:
            original_filename = result['original_filename']
            file_type = result['type']
            logger.info(f"找到檔案記錄: 原始檔名={original_filename}, 類型={file_type}")
        else:
            logger.warning(f"資料庫中找不到檔案記錄: {filename}")
            original_filename = filename
            file_type = Config.get_file_type(filename.split('.')[-1])
    
    # 對於圖片和影片，直接在瀏覽器中預覽
    if file_type in ['image', 'video']:
        logger.info(f"提供檔案預覽: {file_type}")
        return FileResponse(
            str(file_location),
            media_type=f"{file_type}/{filename.split('.')[-1].lower()}"
        )
    
    # 其他類型的檔案提供下載
    logger.info(f"提供檔案下載: {original_filename}")
    return FileResponse(
        str(file_location),
        filename=original_filename,
        media_type='application/octet-stream'
    )

@router.get("/all/")
async def get_all_files():
    """
    獲取所有已上傳的檔案列表
    
    Returns:
        - **files**: 檔案列表，包含完整資訊
    """
    try:
        logger.info("開始獲取所有檔案列表")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, url, filename, original_filename, size, type, created_at 
                FROM files 
                ORDER BY created_at DESC
            """)
            files = [dict(row) for row in cursor.fetchall()]
            
            logger.info(f"成功獲取檔案列表，數量: {len(files)}")
            logger.debug(f"檔案列表詳情: {files}")
            return {"files": files}
    except Exception as e:
        logger.error(f"獲取檔案列表失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(file_id: int):
    """
    刪除檔案
    
    - **file_id**: 要刪除的檔案ID
    """
    try:
        logger.info(f"開始刪除檔案 ID: {file_id}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 先獲取檔案資訊
            cursor.execute("SELECT filename, original_filename FROM files WHERE id = ?", (file_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"找不到要刪除的檔案 ID: {file_id}")
                raise HTTPException(status_code=404, detail="File not found")
            
            filename = result['filename']
            original_filename = result['original_filename']
            logger.info(f"準備刪除檔案: {filename} (原始檔名: {original_filename})")
            
            file_path = Path(Config.UPLOAD_FOLDER) / filename
            
            # 刪除實體檔案
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已刪除實體檔案: {file_path}")
            else:
                logger.warning(f"實體檔案不存在: {file_path}")
            
            # 從資料庫中刪除記錄
            cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()
            logger.info(f"已從資料庫中刪除檔案記錄")
            
            return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除檔案失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))