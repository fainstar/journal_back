# 日記本系統 API 文件

## 基本信息

- **基礎URL**: `http://127.0.0.1:8000`
- **版本**: 1.0.0
- **文件**: `/docs` (Swagger UI) 或 `/redoc` (ReDoc)

## 通用結構

所有 API 回應皆使用 JSON 格式，錯誤會以 HTTP 狀態碼和 JSON 物件返回：

```json
{
  "detail": "錯誤訊息"
}
```

## 模組化設計

系統採用模組化設計，API 路由分為以下幾個模組：

1. **圖片管理** (`/images`)
2. **文章管理** (`/notes`)
3. **標籤管理** (`/tags`)

## 圖片管理 API

### 上傳圖片

- **端點**: `POST /images/upload/`
- **描述**: 上傳新圖片
- **請求體**: Form-data 格式
  - `file`: 圖片檔案
- **回應**:
  ```json
  {
    "url": "http://127.0.0.1:8000/images/get/[filename]"
  }
  ```

### 獲取圖片

- **端點**: `GET /images/get/{filename}`
- **描述**: 獲取已上傳的圖片
- **參數**:
  - `filename`: 圖片檔名
- **回應**: 圖片檔案

### 獲取所有圖片

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