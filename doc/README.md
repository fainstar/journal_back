# 日記本項目

## 項目簡介
日記本管理系統是一個基於Web的應用程序，允許用戶上傳圖片、撰寫和保存Markdown格式的日記，並管理所有上傳的內容。系統提供直觀的用戶界面和完整的API支持。

## 主要功能
- 圖片上傳與管理
- Markdown編輯與保存
- 圖片和文章列表查看
- 響應式設計，支持多種設備
- API 文件自動生成（支援 Swagger UI 和 ReDoc）
- 支援 CORS，方便前後端分離開發
- 完整的日誌與異常追蹤系統

## 技術棧
- 後端：FastAPI
- 前端：HTML5, JavaScript, Material Components Web
- 數據庫：SQLite
- Markdown解析：marked.js

## 進階功能

### API 文件
- 訪問 `/docs` 查看 Swagger UI 互動式文件
- 訪問 `/redoc` 查看 ReDoc 格式文件
- 所有 API 端點都帶有詳細的參數說明和響應示例

### CORS 支援
- 支援跨域請求
- 允許所有來源訪問
- 支援各種 HTTP 方法
- 方便前後端分離開發

### 日誌系統
- 自動記錄所有 API 調用
- 錯誤追蹤和異常處理
- 日誌文件：`app.log`
- 包含時間戳和詳細信息

## 使用指南
1. 啟動FastAPI服務：`uvicorn test:app --reload`
2. 打開瀏覽器訪問 `http://127.0.0.1:8000`
3. 使用前端界面測試各項功能
4. 查看 API 文件：訪問 `http://127.0.0.1:8000/docs`
5. 檢查系統日誌：查看 `app.log` 文件