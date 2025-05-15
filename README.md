# 多媒體日記本系統

一個功能完整的多媒體日記本系統，整合 Markdown 編輯、多媒體檔案管理、標籤分類和分享功能。適合個人筆記、團隊協作和檔案分享使用。

## 系統特色

### 內容創作與管理
- 完整的 Markdown 編輯器
  - 即時預覽功能
  - 支援完整 Markdown 語法
  - 自動儲存功能
- 智慧標籤系統
  - 靈活的標籤管理
  - 快速檢索功能
  - 多層級分類

### 多媒體支援
- 全方位檔案支援
  - 圖片：jpg, jpeg, png, gif, webp
  - 影片：mp4, webm, ogg
  - 音訊：mp3, wav
  - 文件：pdf, doc, docx, txt
  - 壓縮檔：zip, 7z, rar

- 進階媒體功能
  - 圖片自適應顯示
  - 影片串流播放
  - 檔案即時預覽
  - 大檔案支援（最大 100MB）

##### 分享與協作
- 進階分享功能
  - 一鍵產生分享連結
  - 直接媒體預覽
  - 快速檔案下載
  - 自動判斷檔案類型
- 安全控制
  - 檔案類型驗證
  - 大小限制保護
  - 存取權限管理

## 技術架構

### 後端技術
- Python 3.10+
  - FastAPI (異步 API 框架)
  - SQLite3 (本地資料庫)
  - uvicorn (高效能伺服器)

### 前端技術
- 現代化框架
  - Material Design Components
  - 響應式設計
  - 跨裝置支援
- 進階功能
  - Marked.js (Markdown 引擎)
  - Media API (多媒體處理)
  - 檔案處理系統

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

## 系統架構

```
journal_back/
├── app.py              # 主應用程式
├── common.py           # 共用功能和配置
├── requirements.txt    # 依賴套件
├── docker-compose.yml  # Docker 配置
├── Dockerfile         # Docker 建構檔
├── routers/           # API 路由
│   ├── files.py      # 檔案管理
│   ├── images.py     # 圖片處理
│   ├── notes.py      # 文章管理
│   ├── share.py      # 分享功能
│   └── tags.py       # 標籤管理
├── static/           # 靜態資源
│   ├── js/          # JavaScript 檔案
│   │   └── app.js   # 前端邏輯
│   └── templates/    # HTML 模板
│       ├── base.html    # 基礎模板
│       ├── files.html   # 檔案管理
│       ├── images.html  # 圖片管理
│       ├── index.html   # 首頁
│       └── notes.html   # 筆記編輯
├── uploads/          # 上傳檔案儲存
│   └── files/       # 檔案存儲目錄
└── doc/             # 文件
    ├── API.md       # API 文件
    ├── Design.md    # 設計文件
    └── markdown_guide.md # Markdown 指南
```

## 快速開始

### 環境需求
- Python 3.10+
- 現代瀏覽器（支援 ES6+）
- 500MB 以上硬碟空間

### 安裝步驟

1. 克隆專案：
```powershell
git clone [repository-url]
cd journal_back
```

2. 安裝依賴：
```powershell
pip install -r requirements.txt
```

3. 啟動伺服器：
```powershell
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Docker 部署
```powershell
docker-compose up -d
```

## 文件
- [API 文件](doc/API.md) - API 使用說明和範例
- [設計文件](doc/Design.md) - 系統架構和設計原理

## 更新日誌

### v1.2.0 (2025-05-15)
#### 新功能
- 檔案分享系統
  - 一鍵生成分享連結
  - 自動判斷檔案類型
  - 直接媒體預覽
- 安全性增強
  - 檔案類型驗證
  - 訪問控制優化
  - 錯誤處理改進
- 使用者體驗優化
  - UI/UX改進
  - 效能提升
  - 回應速度優化

### v1.1.0 (2024-01-19)
- 新增影片預覽功能
- 統一檔案管理介面
- 改進多媒體支援
- 添加鍵盤快捷鍵

### v1.0.0 (2024-01-01)
- 首次發布
- 基礎功能實現
- Markdown 支援
- 檔案管理系統

## 授權
本專案採用 MIT 授權條款。

## 開發團隊
- 作者：Multimedia Journal System Team
- 版本：1.2.0
- 最後更新：2025-05-15