# 日記本項目

## 項目簡介
日記本管理系統是一個基於Web的應用程序，允許用戶上傳圖片、撰寫和保存Markdown格式的日記，並管理所有上傳的內容。系統提供直觀的用戶界面和完整的API支持。

## 主要功能
- 圖片上傳與管理
- Markdown編輯與保存
- 圖片和文章列表查看
- 自訂圖片尺寸控制
- 響應式設計，支持多種設備
- API 文件自動生成（支援 Swagger UI 和 ReDoc）
- 支援 CORS，方便前後端分離開發
- 完整的日誌與異常追蹤系統
- 模板系統，支援頁面組件化開發

## 技術棧
- 後端：FastAPI (Python 3.10+)
- 前端：HTML5, JavaScript, Material Components Web, Jinja2 模板引擎
- 數據庫：SQLite
- Markdown解析：marked.js
- 圖片處理：支援自訂尺寸和錯誤處理

## 項目結構
```
journal_back/
├── app.py           # 主應用程序入口
├── common.py        # 共用函數與設定
├── diary.db         # SQLite 數據庫文件
├── requirements.txt # 依賴項目清單
│
├── templates/       # 模板文件夾
│   ├── base.html    # 基礎模板
│   ├── index.html   # 主頁模板
│   ├── images.html  # 圖片管理模板
│   └── notes.html   # 文章管理模板
│
├── static/          # 靜態資源文件夾
│   └── js/
│       └── app.js   # 前端 JavaScript 代碼
│
├── routers/         # API 路由模組
│   ├── images.py    # 圖片相關 API
│   ├── notes.py     # 文章相關 API
│   └── tags.py      # 標籤相關 API
│
├── uploads/         # 上傳文件儲存目錄
│   └── images/      # 圖片儲存目錄
│
└── doc/             # 文檔目錄
    ├── API.md       # API 文檔
    ├── markdown_guide.md # Markdown 使用指南
    └── README.md    # 項目說明文檔
```

## 最新功能
- **模板系統**：使用 Jinja2 模板引擎，實現頁面組件化開發
- **圖片尺寸控制**：在 Markdown 中可使用 `![描述](圖片.jpg =寬度x高度)` 格式控制圖片尺寸
- **強化錯誤處理**：圖片加載失敗時顯示友好的錯誤提示
- **表格支援**：完整支援 Markdown 表格語法
- **安全性增強**：更嚴格的參數檢查和類型驗證

## 進階功能

### 模板系統
- 基於 Jinja2 的模板引擎
- 頁面組件化開發
- 易於維護和擴展
- 支援模板繼承和包含

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

### 圖片管理系統
- 支援多種圖片格式 (JPG, PNG, GIF, WEBP 等)
- 基於 MD5 哈希的圖片命名，防止重複上傳
- 自動縮放顯示，適應各種螢幕尺寸
- 圖片刪除時同時清理數據庫和文件系統

## 使用指南
1. 安裝依賴項：`pip install -r requirements.txt`
2. 啟動FastAPI服務：`uvicorn app:app --reload`
3. 打開瀏覽器訪問 `http://127.0.0.1:8000`
4. 使用前端界面測試各項功能
5. 查看 API 文件：訪問 `http://127.0.0.1:8000/docs`
6. 檢查系統日誌：查看 `app.log` 文件

## 系統要求
- Python 3.10 或更高版本
- FastAPI 0.95.0+
- Jinja2 3.1.2+
- 推薦使用現代瀏覽器（Chrome、Firefox、Edge 等）


## 開發&部屬指南
- docker build -t oomaybeoo/journal-back:latest .
- docker push oomaybeoo/journal-back:latest
- docker pull oomaybeoo/journal-back:latest
- docker run -p 8000:8000 -d oomaybeoo/journal-back:latest

## 未來方向
- **遷移至 IPFS**：將圖片、內文等檔案儲存遷移至星際檔案系統 (IPFS)，以實現去中心化儲存。
- **檔案空間管理**：新增管理用戶檔案儲存空間的功能。

## 更新日期
2025 年 5 月 6 日