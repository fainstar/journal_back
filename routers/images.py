from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import hashlib
import os
from pathlib import Path
import sys

# 從common模組導入相關功能
from common import get_db_connection, Config, logger

router = APIRouter(
    prefix="/images",
    tags=["圖片管理"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    """
    上傳圖片檔案
    
    - **file**: 要上傳的圖片檔案（支援常見圖片格式）
    
    Returns:
        - **url**: 上傳後的圖片 URL
    """
    try:
        # 驗證檔案類型
        file_extension = Path(file.filename).suffix.lower()[1:]  # 去掉開頭的點
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"不支援的檔案類型: {file_extension}")
            
        # 計算檔案hash值
        file_content = await file.read()
        file_hash = hashlib.md5(file_content).hexdigest()
        file_extension = Path(file.filename).suffix
        
        # 儲存圖片
        file_location = Path(Config.UPLOAD_FOLDER) / f"{file_hash}{file_extension}"
        with open(file_location, "wb") as f:
            f.write(file_content)
        
        # 儲存圖片URL到數據庫
        image_url = f"http://127.0.0.1:8000/images/get/{file_hash}{file_extension}"
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

@router.get("/get/{filename}")
async def get_image(filename: str):
    """
    獲取上傳的圖片
    """
    file_location = Path(Config.UPLOAD_FOLDER) / filename
    if not file_location.exists():
        return JSONResponse(
            status_code=404,
            content={"message": "Image not found"}
        )
    return FileResponse(str(file_location))

@router.get("/all/")
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
            
            # 將行結果轉換為列表格式，確保前端能正確處理
            result = cursor.fetchall()
            images = []
            for row in result:
                # 如果是 Row 對象，轉換為列表
                if hasattr(row, 'keys'):
                    images.append([row['url'], row['filename']])
                else:
                    images.append(row)  # 已經是列表或元組格式
            
            # 調試日誌
            logger.info(f"成功獲取圖片列表，數量: {len(images)}")
            
            # 檢查第一個結果的格式（如果有）
            if images and len(images) > 0:
                logger.info(f"第一個圖片格式範例: {images[0]}")
                
        return {"images": images}
    except Exception as e:
        logger.error(f"獲取圖片列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{filename}")
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

@router.get("/info/{filename}")
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