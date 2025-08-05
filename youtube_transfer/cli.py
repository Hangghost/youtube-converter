"""
YouTube to MP3 Converter CLI

Command-line interface for downloading YouTube videos and converting to MP3.
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional

import click
import yt_dlp
from pydub import AudioSegment


class YouTubeToMP3Converter:
    """YouTube to MP3 converter class."""
    
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def validate_youtube_url(self, url: str) -> bool:
        """驗證 YouTube URL 格式."""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&.*)?',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+(?:&.*)?',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+(?:&.*)?',
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def get_video_info(self, url: str) -> Optional[dict]:
        """獲取影片資訊."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 10,  # 10 秒超時
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                click.echo("🔍 正在獲取影片資訊...")
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                }
        except Exception as e:
            click.echo(f"❌ 無法獲取影片資訊: {e}", err=True)
            return None
    
    def download_and_convert(self, url: str, quality: str = "best") -> bool:
        """下載影片並轉換為 MP3."""
        if not self.validate_youtube_url(url):
            click.echo("❌ 無效的 YouTube URL", err=True)
            return False
        
        # 獲取影片資訊
        info = self.get_video_info(url)
        if not info:
            return False
        
        click.echo(f"📹 影片標題: {info['title']}")
        click.echo(f"👤 上傳者: {info['uploader']}")
        
        # 設定下載選項
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [self._progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                click.echo("🚀 開始下載並轉換...")
                ydl.download([url])
            
            click.echo("✅ 下載完成！")
            return True
            
        except Exception as e:
            click.echo(f"❌ 下載失敗: {e}", err=True)
            return False
    
    def _progress_hook(self, d):
        """下載進度回調."""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                click.echo(f"\r📥 下載進度: {percent:.1f}%", nl=False)
        elif d['status'] == 'finished':
            click.echo("\n🔄 開始轉換為 MP3...")


@click.command()
@click.argument('url', required=True)
@click.option('--output-dir', '-o', default='downloads', 
              help='輸出目錄 (預設: downloads)')
@click.option('--quality', '-q', default='192', 
              help='MP3 音質 (預設: 192)')
@click.version_option(version='0.1.0')
def main(url: str, output_dir: str, quality: str):
    """
    YouTube 轉 MP3 下載器
    
    使用範例:
        python -m youtube_transfer.cli "https://www.youtube.com/watch?v=VIDEO_ID"
        python -m youtube_transfer.cli "https://www.youtube.com/watch?v=VIDEO_ID" -o my_music
    """
    click.echo("🎵 YouTube 轉 MP3 下載器")
    click.echo("=" * 40)
    
    # 檢查 FFmpeg
    if not _check_ffmpeg():
        click.echo("❌ 需要安裝 FFmpeg 才能轉換音訊格式", err=True)
        click.echo("請安裝 FFmpeg: https://ffmpeg.org/download.html", err=True)
        sys.exit(1)
    
    # 建立轉換器
    converter = YouTubeToMP3Converter(output_dir)
    
    # 開始下載
    success = converter.download_and_convert(url, quality)
    
    if success:
        click.echo(f"📁 檔案已儲存至: {output_dir}")
    else:
        sys.exit(1)


def _check_ffmpeg() -> bool:
    """檢查 FFmpeg 是否已安裝."""
    import subprocess
    try:
        # 使用 timeout 避免卡住
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              timeout=5)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


if __name__ == '__main__':
    main() 