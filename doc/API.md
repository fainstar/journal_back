# 日記本系統 API 文件

## 基本信息

- **基礎 URL**: `http://localhost:8000`
- **API 版本**: v1.2.0
- **回應格式**: JSON
- **編碼方式**: UTF-8
- **API 文件**: `/docs` (Swagger UI) 或 `/redoc` (ReDoc)

## API 端點總覽

### 文章管理 API
- `POST /notes/create/` - 建立新文章
- `GET /notes/all/` - 獲取文章列表
- `GET /notes/{note_id}` - 取得指定文章
- `PUT /notes/{note_id}` - 更新文章內容
- `DELETE /notes/{note_id}` - 刪除文章

### 檔案管理 API
- `POST /files/upload/` - 上傳檔案
- `GET /files/all/` - 取得檔案列表
- `GET /files/download/{filename}` - 下載檔案
- `DELETE /files/{file_id}` - 刪除檔案

### 圖片管理 API
- `POST /images/upload/` - 上傳圖片
- `GET /images/all/` - 獲取圖片列表
- `GET /images/get/{filename}` - 取得圖片
- `DELETE /images/delete/{filename}` - 刪除圖片

### 分享功能 API
- `POST /share/create/{file_id}` - 建立分享連結
- `GET /share/{share_code}` - 存取分享內容

## 安全性說明

### 檔案上傳限制
- 最大檔案大小: 100MB
- 支援的檔案類型:
  - 圖片: jpg, jpeg, png, gif, webp
  - 影片: mp4, webm, ogg
  - 音訊: mp3, wav
  - 文件: pdf, doc, docx, txt
  - 壓縮: zip, 7z, rar

### 資料驗證
- 所有上傳檔案都進行類型驗證
- Markdown 內容使用 Base64 編碼
- 檔案名稱安全處理
- SQL 注入防護

## 錯誤處理

所有 API 錯誤會以標準格式返回：

```json
{
  "detail": "錯誤訊息描述"
}
```

### HTTP 狀態碼
- 200: 請求成功
- 400: 請求參數錯誤
- 401: 未授權訪問
- 404: 資源不存在
- 500: 伺服器內部錯誤

## API 詳細說明

### 檔案分享功能

#### 建立分享連結
- **端點**: `POST /share/create/{file_id}`
- **描述**: 為檔案創建分享連結
- **參數**:
  - `file_id`: 要分享的檔案ID
- **成功回應** (200):
  ```json
  {
    "share_code": "隨機生成的分享代碼",
    "url": "/share/分享代碼"
  }
  ```

#### 存取分享內容
- **端點**: `GET /share/{share_code}`
- **描述**: 存取分享的檔案內容
- **參數**:
  - `share_code`: 分享代碼
- **回應**: 
  - 圖片/影片: 直接顯示預覽
  - 其他檔案: 直接下載
- **錯誤回應** (404):
  ```json
  {
    "detail": "Shared file not found"
  }
  ```

### 檔案管理

#### 上傳檔案
- **端點**: `POST /files/upload/`
- **描述**: 上傳任意類型檔案
- **請求格式**: `multipart/form-data`
- **參數**:
  - `file`: 檔案資料
- **成功回應** (200):
  ```json
  {
    "filename": "儲存的檔名",
    "original_filename": "原始檔名",
    "size": 1024,
    "type": "檔案類型"
  }
  ```

- **端點**: `GET /images/all/`
- **描述**: 獲取所有已上傳的圖片
- **回應**:
  ```json
  {
    "images": [
      ["http://127.0.0.1:8000/images/get/image1.jpg", "image1.jpg"],
      ["http://127.0.0.1:8000/images/get/image2.jpg", "image2.jpg"]
    ]
  }
  ```

### 刪除圖片

- **端點**: `DELETE /images/delete/{filename}`
- **描述**: 刪除指定圖片
- **參數**:
  - `filename`: 圖片檔名
- **回應**:
  ```json
  {
    "message": "Image deleted successfully"
  }
  ```

### 獲取圖片信息

- **端點**: `GET /images/info/{filename}`
- **描述**: 獲取指定圖片的詳細信息
- **參數**:
  - `filename`: 圖片檔名
- **回應**:
  ```json
  {
    "image": ["http://127.0.0.1:8000/images/get/image1.jpg", "image1.jpg", "2025-05-05T12:00:00"]
  }
  ```

## 文章管理 API

### 建立文章

- **端點**: `POST /notes/create/`
- **描述**: 建立新文章
- **請求體**:
  ```json
  {
    "content": "base64編碼的內容",
    "tags": ["標籤1", "標籤2"]  // 可選
  }
  ```
- **回應**:
  ```json
  {
    "message": "Markdown saved to database successfully!",
    "note_id": 123,
    "content_length": 256
  }
  ```

### 獲取所有文章

- **端點**: `GET /notes/all/`
- **描述**: 獲取所有文章列表
- **參數**:
  - `tag`: (可選) 按標籤過濾
  - `limit`: (可選) 每頁數量，預設 50
  - `offset`: (可選) 分頁偏移，預設 0
- **回應**:
  ```json
  {
    "notes": [
      {
        "id": 1,
        "content": "文章內容",
        "created_at": "2025-05-05T12:00:00",
        "tags": ["標籤1", "標籤2"]
      }
    ],
    "total": 100
  }
  ```

### 獲取單篇文章

- **端點**: `GET /notes/{note_id}`
- **描述**: 獲取指定文章
- **參數**:
  - `note_id`: 文章ID
- **回應**:
  ```json
  {
    "note": {
      "id": 1,
      "content": "文章內容",
      "created_at": "2025-05-05T12:00:00",
      "tags": ["標籤1", "標籤2"]
    }
  }
  ```

### 更新文章

- **端點**: `PUT /notes/{note_id}`
- **描述**: 更新指定文章
- **參數**:
  - `note_id`: 文章ID
- **請求體**:
  ```json
  {
    "content": "base64編碼的新內容",
    "tags": ["新標籤1", "新標籤2"]  // 可選，更新標籤
  }
  ```
- **回應**:
  ```json
  {
    "message": "Note updated successfully"
  }
  ```

### 刪除文章

- **端點**: `DELETE /notes/{note_id}`
- **描述**: 刪除指定文章
- **參數**:
  - `note_id`: 文章ID
- **回應**:
  ```json
  {
    "message": "Note deleted successfully"
  }
  ```

## 標籤管理 API

### 獲取所有標籤

- **端點**: `GET /tags/all/`
- **描述**: 獲取所有標籤列表
- **回應**:
  ```json
  {
    "tags": [
      {
        "id": 1,
        "name": "標籤1",
        "note_count": 10
      },
      {
        "id": 2,
        "name": "標籤2",
        "note_count": 5
      }
    ]
  }
  ```

### 搜尋標籤

- **端點**: `GET /tags/search/`
- **描述**: 按名稱搜尋標籤
- **參數**:
  - `query`: 搜尋關鍵字
- **回應**: 同 `GET /tags/all/`

### 刪除標籤

- **端點**: `DELETE /tags/{tag_id}`
- **描述**: 刪除標籤及其關聯
- **參數**:
  - `tag_id`: 標籤ID
- **回應**:
  ```json
  {
    "message": "Tag deleted successfully"
  }
  ```

### 更新標籤

- **端點**: `PUT /tags/{tag_id}`
- **描述**: 更新標籤名稱
- **參數**:
  - `tag_id`: 標籤ID
- **請求體**:
  ```json
  {
    "name": "新標籤名稱"
  }
  ```
- **回應**:
  ```json
  {
    "message": "Tag updated successfully"
  }
  ```

### 獲取標籤相關文章

- **端點**: `GET /tags/{tag_id}/notes/`
- **描述**: 獲取包含特定標籤的文章列表
- **參數**:
  - `tag_id`: 標籤ID
  - `limit`: (可選) 每頁數量，預設 50
  - `offset`: (可選) 分頁偏移，預設 0
- **回應**:
  ```json
  {
    "notes": [
      {
        "id": 1,
        "content": "文章內容",
        "created_at": "2025-05-05T12:00:00",
        "tags": [
          {"id": 1, "name": "標籤1"},
          {"id": 2, "name": "標籤2"}
        ]
      }
    ],
    "total": 5,
    "tag": {
      "id": 1,
      "name": "標籤1"
    }
  }
  ```

## 系統管理 API

### 健康檢查

- **端點**: `GET /health`
- **描述**: 系統健康狀態檢查
- **回應**:
  ```json
  {
    "status": "ok",
    "version": "1.0.0"
  }
  ```