# YouTube 轉 MP3 下載器

一個簡單的命令列工具，用於下載 YouTube 影片並轉換為 MP3 格式。

## ⚠️ 重要聲明

本工具僅供個人學習和合法授權內容使用。請遵守：
- YouTube 服務條款
- 版權法規
- 僅下載您有權使用的內容

## 功能特色

- 🎵 支援多種 YouTube URL 格式
- 📁 自訂輸出目錄
- 🎚️ 可調整 MP3 音質
- 📊 即時下載進度顯示
- ✅ 自動驗證 URL 格式
- 🔄 自動轉換為 MP3 格式

## 安裝需求

### 1. 安裝 FFmpeg

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

### 基本使用

```bash
# 使用 Poetry 執行
poetry run python -m youtube_transfer.cli "https://www.youtube.com/watch?v=VIDEO_ID"

# 或直接執行
python -m youtube_transfer.cli "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 進階選項

```bash
# 指定輸出目錄
poetry run python -m youtube_transfer.cli "URL" -o my_music

# 調整音質 (預設: 192)
poetry run python -m youtube_transfer.cli "URL" -q 320

# 查看版本
poetry run python -m youtube_transfer.cli --version

# 查看幫助
poetry run python -m youtube_transfer.cli --help
```

## 支援的 URL 格式

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## 專案結構

```
youtube_transfer/
├── __init__.py          # 套件初始化
├── cli.py              # 主要 CLI 程式
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
1. FFmpeg 是否正確安裝
2. 網路連線是否正常
3. YouTube URL 是否有效
4. 是否有足夠的磁碟空間 