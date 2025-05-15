# 日記本系統

一個現代化的多媒體日記本系統，支援 Markdown 編輯、多媒體檔案管理、標籤系統等功能。

## 功能特點

### 內容管理
- Markdown 編輯與即時預覽
- 支援圖片、影片、音訊等多媒體內容
- 標籤系統，便於內容分類
- 檔案管理系統，支援多種格式

### 檔案支援
- 圖片：jpg, jpeg, png, gif, webp
- 影片：mp4, webm, ogg
- 音訊：mp3, wav
- 文件：pdf, doc, docx, txt
- 壓縮檔：zip, 7z, rar

### 技術特色
- FastAPI 後端，提供高效能 API
- 現代化的前端界面，使用 Material Design
- 響應式設計，支援多種設備
- 實時預覽和播放功能
- 完整的錯誤處理和日誌系統

## 技術棧

### 後端
- Python 3.10+
- FastAPI
- SQLite3
- uvicorn

### 前端
- HTML5/CSS3
- JavaScript (原生)
- Material Design Components
- Marked.js (Markdown 渲染)

## 系統需求
- Python 3.10 或更高版本
- 現代瀏覽器 (支援 HTML5)
- 500MB 以上硬碟空間

## 快速開始

1. 克隆專案：
```bash
git clone [repository-url]
cd journal_back
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 啟動伺服器：
```bash
uvicorn app:app --reload
```

4. 開啟瀏覽器訪問：
```
http://localhost:8000
```

## 專案結構

```
journal_back/
├── app.py              # 主應用程式
├── common.py           # 共用功能和配置
├── requirements.txt    # 依賴套件
├── routers/           # API 路由
│   ├── files.py      # 檔案管理
│   ├── notes.py      # 文章管理
│   └── tags.py       # 標籤管理
├── static/           # 靜態資源
│   ├── js/          # JavaScript 檔案
│   └── templates/    # HTML 模板
├── uploads/         # 上傳檔案儲存
└── doc/            # 文件
    ├── API.md      # API 文件
    └── Design.md   # 設計文件
```

## 文件
- [API 文件](doc/API.md)
- [設計文件](doc/Design.md)
- [Markdown 指南](doc/markdown_guide.md)

## 授權
本專案採用 MIT 授權條款。

## 開發者
- 作者：[您的名字]
- 版本：1.0.0