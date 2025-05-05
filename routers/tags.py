from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import sys

# 從common模組導入相關功能
from common import get_db_connection, logger

router = APIRouter(
    prefix="/tags",
    tags=["標籤管理"],
    responses={404: {"description": "Not found"}},
)

@router.get("/all/")
async def get_all_tags():
    """
    獲取所有標籤列表
    
    Returns:
        - **tags**: 標籤列表
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.name, COUNT(nt.note_id) as note_count
                FROM tags t
                LEFT JOIN note_tags nt ON t.id = nt.tag_id
                GROUP BY t.id
                ORDER BY note_count DESC, t.name ASC
            """)
            
            tags = []
            for row in cursor:
                tags.append({
                    "id": row[0],
                    "name": row[1],
                    "note_count": row[2]
                })
            
        logger.info("成功獲取所有標籤列表")
        return {"tags": tags}
    except Exception as e:
        logger.error(f"獲取標籤列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/")
async def search_tags(query: str = ""):
    """
    搜尋標籤
    
    - **query**: 搜尋關鍵字
    
    Returns:
        - **tags**: 符合的標籤列表
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.name, COUNT(nt.note_id) as note_count
                FROM tags t
                LEFT JOIN note_tags nt ON t.id = nt.tag_id
                WHERE t.name LIKE ?
                GROUP BY t.id
                ORDER BY note_count DESC, t.name ASC
                LIMIT 20
            """, (f"%{query}%",))
            
            tags = []
            for row in cursor:
                tags.append({
                    "id": row[0],
                    "name": row[1],
                    "note_count": row[2]
                })
            
        return {"tags": tags}
    except Exception as e:
        logger.error(f"搜尋標籤失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{tag_id}")
async def delete_tag(tag_id: int):
    """
    刪除標籤
    
    - 刪除標籤會自動刪除與文章的關聯，但不會刪除文章本身
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 刪除標籤關聯
            cursor.execute("DELETE FROM note_tags WHERE tag_id = ?", (tag_id,))
            
            # 刪除標籤
            cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
            
            if cursor.rowcount == 0:
                return JSONResponse(
                    status_code=404,
                    content={"message": "Tag not found"}
                )
                
            conn.commit()
        
        return {"message": "Tag deleted successfully"}
    except Exception as e:
        logger.error(f"刪除標籤失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{tag_id}")
async def update_tag(tag_id: int, data: dict):
    """
    更新標籤名稱
    
    - **name**: 新標籤名稱
    """
    try:
        if "name" not in data or not data["name"].strip():
            raise HTTPException(status_code=400, detail="標籤名稱不能為空")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 更新標籤
            cursor.execute("UPDATE tags SET name = ? WHERE id = ?", (data["name"], tag_id))
            
            if cursor.rowcount == 0:
                return JSONResponse(
                    status_code=404,
                    content={"message": "Tag not found"}
                )
                
            conn.commit()
        
        return {"message": "Tag updated successfully"}
    except Exception as e:
        logger.error(f"更新標籤失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tag_id}/notes/")
async def get_tag_notes(tag_id: int, limit: int = 50, offset: int = 0):
    """
    獲取包含特定標籤的文章列表
    
    Returns:
        - **notes**: 文章列表
        - **total**: 總記錄數
        - **tag**: 標籤資訊
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 獲取標籤資訊
            cursor.execute("SELECT id, name FROM tags WHERE id = ?", (tag_id,))
            tag = cursor.fetchone()
            
            if not tag:
                return JSONResponse(
                    status_code=404, 
                    content={"message": "Tag not found"}
                )
            
            # 獲取文章列表
            query = """
            SELECT n.id, n.content, n.created_at 
            FROM markdown_notes n
            JOIN note_tags nt ON n.id = nt.note_id
            WHERE nt.tag_id = ?
            ORDER BY n.created_at DESC
            LIMIT ? OFFSET ?
            """
            cursor.execute(query, (tag_id, limit, offset))
            
            notes = []
            for row in cursor:
                # 為每篇文章獲取所有標籤
                cursor.execute("""
                SELECT t.id, t.name
                FROM tags t
                JOIN note_tags nt ON t.id = nt.tag_id
                WHERE nt.note_id = ?
                """, (row[0],))
                tags = [{"id": t[0], "name": t[1]} for t in cursor.fetchall()]
                
                # 添加文章和標籤到結果
                notes.append({
                    "id": row[0],
                    "content": row[1],
                    "created_at": row[2],
                    "tags": tags
                })
            
            # 獲取總記錄數
            cursor.execute("""
            SELECT COUNT(*) 
            FROM markdown_notes n
            JOIN note_tags nt ON n.id = nt.note_id
            WHERE nt.tag_id = ?
            """, (tag_id,))
            total = cursor.fetchone()[0]
            
        return {
            "notes": notes, 
            "total": total,
            "tag": {
                "id": tag[0],
                "name": tag[1]
            }
        }
    except Exception as e:
        logger.error(f"獲取標籤相關文章失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))