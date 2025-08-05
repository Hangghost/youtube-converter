# YouTube 下載器

一個功能強大的命令列工具，用於下載 YouTube 影片為 MP4 格式或轉換為 MP3 格式。

## ⚠️ 重要聲明

本工具僅供個人學習和合法授權內容使用。請遵守：
- YouTube 服務條款
- 版權法規
- 僅下載您有權使用的內容

## 功能特色

### 🎬 影片下載功能
- 📹 下載 YouTube 影片為 MP4 格式
- 🎨 支援多種畫質選擇 (1080p, 720p, 480p, 360p)
- 📊 即時下載進度顯示
- ✅ 自動驗證 URL 格式

### 🎵 音訊下載功能
- 🎵 支援多種 YouTube URL 格式
- 📁 自訂輸出目錄
- 🎚️ 可調整 MP3 音質
- 🔄 自動轉換為 MP3 格式

### ℹ️ 資訊查詢功能
- 📋 顯示影片詳細資訊
- 📺 列出可用影片格式
- 🎵 列出可用音訊格式

## 安裝需求

### 1. 安裝 FFmpeg (僅音訊轉換需要)

**macOS (使用 Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
下載並安裝 [FFmpeg](https://ffmpeg.org/download.html)

### 2. 安裝 Python 依賴

```bash
# 安裝 Poetry (如果還沒安裝)
curl -sSL https://install.python-poetry.org | python3 -

# 安裝專案依賴
poetry install
```

## 使用方法

### 🎬 下載影片 (MP4)

```bash
# 下載最佳畫質影片
poetry run python -m youtube_transfer.cli video "https://www.youtube.com/watch?v=VIDEO_ID"

# 指定畫質 (1080p, 720p, 480p, 360p)
poetry run python -m youtube_transfer.cli video "URL" -q 720p

# 指定輸出目錄
poetry run python -m youtube_transfer.cli video "URL" -o my_videos

# 下載最低畫質 (節省空間)
poetry run python -m youtube_transfer.cli video "URL" -q worst
```

### 🎵 下載音訊 (MP3)

```bash
# 下載並轉換為 MP3
poetry run python -m youtube_transfer.cli audio "https://www.youtube.com/watch?v=VIDEO_ID"

# 調整音質
poetry run python -m youtube_transfer.cli audio "URL" -q 320

# 指定輸出目錄
poetry run python -m youtube_transfer.cli audio "URL" -o my_music
```

### ℹ️ 查詢影片資訊

```bash
# 顯示影片資訊和可用格式
poetry run python -m youtube_transfer.cli info "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 📋 查看幫助

```bash
# 查看所有命令
poetry run python -m youtube_transfer.cli --help

# 查看特定命令幫助
poetry run python -m youtube_transfer.cli video --help
poetry run python -m youtube_transfer.cli audio --help
poetry run python -m youtube_transfer.cli info --help
```

## 支援的 URL 格式

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## 畫質選項

### 影片畫質
- `best` - 最佳畫質 (預設)
- `1080p` - 1080p 或更低
- `720p` - 720p 或更低
- `480p` - 480p 或更低
- `360p` - 360p 或更低
- `worst` - 最低畫質

### 音訊品質
- `192` - 192kbps (預設)
- `320` - 320kbps (高品質)
- `128` - 128kbps (節省空間)

## 專案結構

```
youtube_transfer/
├── __init__.py          # 套件初始化
├── cli.py              # 主要 CLI 程式
├── downloads/           # 下載檔案目錄
└── README.md           # 說明文件
```

## 開發

### 設定開發環境

```bash
# 安裝開發依賴
poetry install

# 進入虛擬環境
poetry shell

# 執行測試
poetry run python -m youtube_transfer.cli --help
```

### 新增功能

1. 修改 `youtube_transfer/cli.py`
2. 測試功能
3. 更新 README.md

## 授權

本專案僅供學習用途。請遵守相關法律法規。

## 問題回報

如果遇到問題，請檢查：
1. FFmpeg 是否正確安裝 (僅音訊轉換需要)
2. 網路連線是否正常
3. YouTube URL 是否有效
4. 是否有足夠的磁碟空間
5. 影片是否有地區限制 