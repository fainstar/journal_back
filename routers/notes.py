from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import base64
from pathlib import Path
import sys
import json

# 從common模組導入相關功能
from common import get_db_connection, logger

router = APIRouter(
    prefix="/notes",
    tags=["文章管理"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create/")
async def save_markdown(data: dict):
    """
    建立新文章
    
    - **content**: Base64 編碼的 Markdown 內容
    - **tags**: 可選，標籤列表
    
    Returns:
        - **message**: 成功訊息
        - **note_id**: 文章 ID
        - **content_length**: 內容長度
    """
    try:
        if "content" not in data:
            raise HTTPException(status_code=400, detail="Missing content field")
        
        # 解碼base64內容
        try:
            content = base64.b64decode(data["content"].encode('utf-8')).decode('utf-8')
        except Exception as e:
            logger.error(f"Base64解碼失敗: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid base64 content: {str(e)}")
            
        if not content:
            raise HTTPException(status_code=400, detail="Empty content after decoding")
            
        logger.info(f"成功解碼文章內容，長度: {len(content)}")
        
        # 連接SQLite資料庫
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # 插入文章內容
                cursor.execute("INSERT INTO markdown_notes (content) VALUES (?)", (content,))
                note_id = cursor.lastrowid
                logger.info(f"成功插入文章，ID: {note_id}")
                
                # 處理標籤
                if "tags" in data and isinstance(data["tags"], list) and data["tags"]:
                    for tag_name in data["tags"]:
                        # 插入標籤(如不存在)
                        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                        # 獲取標籤ID
                        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                        tag_id = cursor.fetchone()[0]
                        # 建立關聯
                        cursor.execute("INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)", 
                                     (note_id, tag_id))
                        logger.info(f"添加標籤 '{tag_name}' 到文章 {note_id}")
                
                conn.commit()
                logger.info(f"文章保存完成，ID: {note_id}")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"資料庫操作失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return {
            "message": "Markdown saved to database successfully!",
            "note_id": note_id,
            "content_length": len(content)
        }
    except Exception as e:
        logger.error(f"保存文章失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all/")
async def get_all_notes(tag: str = None, limit: int = 50, offset: int = 0):
    """
    獲取所有已保存的文章列表
    
    - **tag**: 可選，按標籤過濾
    - **limit**: 可選，每頁數量
    - **offset**: 可選，頁碼
    
    Returns:
        - **notes**: 文章列表，包含 ID、內容和建立時間
        - **total**: 總記錄數
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 如果指定標籤，則進行標籤過濾
            if tag:
                query = """
                SELECT n.id, n.content, n.created_at 
                FROM markdown_notes n
                JOIN note_tags nt ON n.id = nt.note_id
                JOIN tags t ON nt.tag_id = t.id
                WHERE t.name = ?
                ORDER BY n.created_at DESC
                LIMIT ? OFFSET ?
                """
                cursor.execute(query, (tag, limit, offset))
                
                # 獲取總記錄數
                cursor.execute("""
                SELECT COUNT(*) 
                FROM markdown_notes n
                JOIN note_tags nt ON n.id = nt.note_id
                JOIN tags t ON nt.tag_id = t.id
                WHERE t.name = ?
                """, (tag,))
            else:
                # 不過濾標籤，獲取所有文章
                query = """
                SELECT id, content, created_at 
                FROM markdown_notes 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """
                cursor.execute(query, (limit, offset))
                
                # 獲取總記錄數
                cursor.execute("SELECT COUNT(*) FROM markdown_notes")
                
            total = cursor.fetchone()[0]
            
            # 執行主查詢
            notes = []
            for row in cursor.execute(query, (tag, limit, offset) if tag else (limit, offset)):
                # 為每篇文章獲取標籤
                cursor.execute("""
                SELECT t.name
                FROM tags t
                JOIN note_tags nt ON t.id = nt.tag_id
                WHERE nt.note_id = ?
                """, (row[0],))
                tags = [tag[0] for tag in cursor.fetchall()]
                
                # 添加文章和標籤到結果
                notes.append({
                    "id": row[0],
                    "content": row[1],
                    "created_at": row[2],
                    "tags": tags
                })
            
        logger.info("成功獲取文章列表")
        return {"notes": notes, "total": total}
    except Exception as e:
        logger.error(f"獲取文章列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{note_id}")
async def get_note(note_id: int):
    """
    獲取指定文章
    
    Returns:
        - **note**: 文章資訊
        - **tags**: 文章標籤
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 獲取文章內容
        cursor.execute("SELECT id, content, created_at FROM markdown_notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        
        if not note:
            return JSONResponse(
                status_code=404,
                content={"message": "Note not found"}
            )
            
        # 獲取文章標籤
        cursor.execute("""
        SELECT t.name
        FROM tags t
        JOIN note_tags nt ON t.id = nt.tag_id
        WHERE nt.note_id = ?
        """, (note_id,))
        tags = [tag[0] for tag in cursor.fetchall()]
        
        # 轉換為字典以便添加標籤
        note_dict = {
            "id": note[0],
            "content": note[1],
            "created_at": note[2],
            "tags": tags
        }
    
    return {"note": note_dict}

@router.put("/{note_id}")
async def update_note(note_id: int, data: dict):
    """
    更新指定文章
    
    - **content**: Base64 編碼的 Markdown 內容
    - **tags**: 可選，標籤列表
    """
    try:
        content = base64.b64decode(data["content"]).decode('utf-8')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 更新文章內容
            cursor.execute("UPDATE markdown_notes SET content = ? WHERE id = ?", (content, note_id))
            
            # 如果沒有更新任何行，說明文章不存在
            if cursor.rowcount == 0:
                return JSONResponse(
                    status_code=404,
                    content={"message": "Note not found"}
                )
                
            # 處理標籤更新
            if "tags" in data and isinstance(data["tags"], list):
                # 刪除舊標籤關聯
                cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
                
                # 添加新標籤
                for tag_name in data["tags"]:
                    # 插入標籤(如不存在)
                    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                    # 獲取標籤ID
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                    tag_id = cursor.fetchone()[0]
                    # 建立關聯
                    cursor.execute("INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)", 
                                 (note_id, tag_id))
            
            conn.commit()
        
        return {"message": "Note updated successfully"}
    except Exception as e:
        logger.error(f"更新文章失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{note_id}")
async def delete_note(note_id: int):
    """
    刪除指定文章
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 刪除標籤關聯
            cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
            
            # 刪除文章
            cursor.execute("DELETE FROM markdown_notes WHERE id = ?", (note_id,))
            
            if cursor.rowcount == 0:
                return JSONResponse(
                    status_code=404,
                    content={"message": "Note not found"}
                )
                
            conn.commit()
        
        return {"message": "Note deleted successfully"}
    except Exception as e:
        logger.error(f"刪除文章失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))