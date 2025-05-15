from fastapi import APIRouter, HTTPException
import secrets
from common import get_db_connection, logger

router = APIRouter(
    prefix="/share",
    tags=["分享功能"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create/{file_id}")
async def create_share_link(file_id: int):
    """
    為指定檔案創建分享連結
    
    Returns:
        - **share_code**: 分享代碼
        - **url**: 完整分享連結
    """
    try:
        # 生成隨機分享代碼
        share_code = secrets.token_urlsafe(8)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 檢查檔案是否存在
            cursor.execute("SELECT id FROM files WHERE id = ?", (file_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="File not found")
            
            # 儲存分享記錄
            cursor.execute("""
                INSERT INTO file_shares (file_id, share_code, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (file_id, share_code))
            
            conn.commit()
            
        return {
            "share_code": share_code,
            "url": f"/share/{share_code}"
        }
    except Exception as e:
        logger.error(f"創建分享連結失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{share_code}")
async def get_shared_file(share_code: str):
    """
    獲取分享的檔案，直接提供下載或預覽連結
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT f.id, f.filename, f.original_filename, f.type
                FROM files f
                JOIN file_shares fs ON f.id = fs.file_id
                WHERE fs.share_code = ?
            """, (share_code,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Shared file not found")
            
            file_id, filename, original_filename, file_type = result
            
            # 根據檔案類型重定向到相應的處理路由
            if file_type == 'image':
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=f"/files/download/{filename}", status_code=303)
            elif file_type == 'video':
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=f"/files/download/{filename}", status_code=303)
            else:
                # 其他類型檔案直接下載
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=f"/files/download/{filename}", status_code=303)
    except Exception as e:
        logger.error(f"獲取分享檔案失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
