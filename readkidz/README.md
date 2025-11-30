# ReadKidz Platform

AI 驅動的兒童多媒體故事創作平台

## 功能特點

- **AI 故事生成**: 從簡單提示詞生成完整兒童故事
- **AI 插圖創作**: 60+ 繪畫風格，保持角色一致性 (Character Mat)
- **影片製作**: 一鍵將繪本轉換為動畫影片
- **配音功能**: 180+ 專業配音選項 (ElevenLabs 整合)
- **一鍵發佈**: 直接發佈至 YouTube 和 Amazon KDP

## 技術架構

### 後端
- **框架**: FastAPI (Python)
- **資料庫**: SQLite (開發) / PostgreSQL (生產)
- **AI 服務**:
  - OpenAI GPT-4 / Claude (故事生成)
  - DALL-E 3 (插圖生成)
  - ElevenLabs (語音合成)
- **認證**: OAuth 2.0 (Google)

### 前端
- **框架**: React 18 + TypeScript
- **建置工具**: Vite
- **樣式**: TailwindCSS
- **狀態管理**: Zustand + TanStack Query
- **動畫**: Framer Motion

## 快速開始

### 後端設定

```bash
cd readkidz/backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env 填入您的 API 金鑰

# 啟動開發伺服器
python run.py
```

後端 API 將在 http://localhost:8000 運行
API 文件: http://localhost:8000/docs

### 前端設定

```bash
cd readkidz/frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev
```

前端將在 http://localhost:3000 運行

## 專案結構

```
readkidz/
├── backend/
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 資料庫模型
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # 業務邏輯服務
│   ├── requirements.txt
│   └── run.py
└── frontend/
    ├── src/
    │   ├── components/    # React 元件
    │   ├── contexts/      # 狀態管理
    │   ├── pages/         # 頁面元件
    │   ├── services/      # API 服務
    │   ├── styles/        # 樣式檔案
    │   └── types/         # TypeScript 類型
    ├── package.json
    └── vite.config.ts
```

## API 端點

### 認證
- `POST /api/v1/auth/register` - 註冊
- `POST /api/v1/auth/login` - 登入
- `GET /api/v1/auth/google` - Google OAuth
- `GET /api/v1/auth/me` - 取得當前用戶

### 專案
- `GET /api/v1/projects` - 列出專案
- `POST /api/v1/projects` - 建立專案
- `GET /api/v1/projects/{id}` - 取得專案詳情
- `PUT /api/v1/projects/{id}` - 更新專案
- `DELETE /api/v1/projects/{id}` - 刪除專案

### AI 生成
- `POST /api/v1/generate/story` - 生成故事
- `POST /api/v1/generate/illustration` - 生成插圖
- `POST /api/v1/generate/video` - 生成影片
- `POST /api/v1/generate/audio` - 生成配音
- `POST /api/v1/generate/one-click-video` - 一鍵影片

### 模板
- `GET /api/v1/templates` - 列出模板
- `GET /api/v1/templates/styles` - 列出風格
- `GET /api/v1/templates/voices` - 列出配音選項
- `GET /api/v1/templates/music` - 列出背景音樂

## 定價方案

| 方案 | 價格 | 積分 | 頁數限制 |
|------|------|------|----------|
| 免費 | $0 | 1,500 | 5 頁 |
| 標準 | $10/月 | 12,000 | 40 頁 |
| 專業 | $30/月 | 30,000 | 50 頁 |
| 超級 | $60/月 | 60,000 | 60 頁 |

## 環境變數

| 變數 | 說明 | 必填 |
|------|------|------|
| `SECRET_KEY` | JWT 密鑰 | ✅ |
| `DATABASE_URL` | 資料庫連接字串 | ✅ |
| `OPENAI_API_KEY` | OpenAI API 金鑰 | ✅ |
| `ANTHROPIC_API_KEY` | Anthropic API 金鑰 | 選填 |
| `ELEVENLABS_API_KEY` | ElevenLabs API 金鑰 | 選填 |
| `GOOGLE_CLIENT_ID` | Google OAuth 客戶端 ID | 選填 |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 密鑰 | 選填 |

## 授權

Copyright © 2024 ReadKidz. All rights reserved.
