"""
YouTube to MP3/MP4 Converter CLI

Command-line interface for downloading YouTube videos and converting to MP3 or downloading as MP4.
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict

import click
import yt_dlp
from pydub import AudioSegment


class YouTubeConverter:
    """YouTube converter class for both audio and video downloads."""
    
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
                    'formats': info.get('formats', []),
                }
        except Exception as e:
            click.echo(f"❌ 無法獲取影片資訊: {e}", err=True)
            return None
    
    def get_available_formats(self, url: str) -> Dict[str, List[dict]]:
        """獲取可用的格式和畫質選項."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                # 分類格式
                video_formats = []
                audio_formats = []
                
                for fmt in formats:
                    if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                        # 影片格式（包含音訊）
                        video_formats.append({
                            'format_id': fmt.get('format_id'),
                            'ext': fmt.get('ext'),
                            'resolution': fmt.get('resolution'),
                            'height': fmt.get('height'),
                            'filesize': fmt.get('filesize'),
                            'format_note': fmt.get('format_note', ''),
                        })
                    elif fmt.get('acodec') != 'none':
                        # 純音訊格式
                        audio_formats.append({
                            'format_id': fmt.get('format_id'),
                            'ext': fmt.get('ext'),
                            'abr': fmt.get('abr'),
                            'filesize': fmt.get('filesize'),
                            'format_note': fmt.get('format_note', ''),
                        })
                
                return {
                    'video': video_formats,
                    'audio': audio_formats
                }
        except Exception as e:
            click.echo(f"❌ 無法獲取格式資訊: {e}", err=True)
            return {'video': [], 'audio': []}
    
    def download_video(self, url: str, quality: str = "best") -> bool:
        """下載影片為 MP4 格式."""
        if not self.validate_youtube_url(url):
            click.echo("❌ 無效的 YouTube URL", err=True)
            return False
        
        # 獲取影片資訊
        info = self.get_video_info(url)
        if not info:
            return False
        
        click.echo(f"📹 影片標題: {info['title']}")
        click.echo(f"👤 上傳者: {info['uploader']}")
        
        # 根據畫質選擇格式
        format_selector = self._get_video_format_selector(quality)
        
        # 設定下載選項
        ydl_opts = {
            'format': format_selector,
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                click.echo(f"🚀 開始下載影片 (畫質: {quality})...")
                ydl.download([url])
            
            click.echo("✅ 影片下載完成！")
            return True
            
        except Exception as e:
            click.echo(f"❌ 影片下載失敗: {e}", err=True)
            return False
    
    def download_audio(self, url: str, quality: str = "192", volume: Optional[str] = None) -> bool:
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
                'preferredquality': quality,
            }],
            'progress_hooks': [self._progress_hook],
        }

        # 若指定音量，加入 FFmpeg 濾鏡
        if volume is not None:
            v = volume.strip()
            expr = None
            try:
                if v.lower().endswith('db'):
                    val = float(v[:-2])
                    expr = f"volume={val}dB"
                elif v.endswith('%'):
                    pct = float(v[:-1])
                    expr = f"volume={pct/100.0}"
                elif v.lower().endswith('x'):
                    factor = float(v[:-1])
                    expr = f"volume={factor}"
                else:
                    factor = float(v)
                    expr = f"volume={factor}"
            except ValueError:
                click.echo("❌ 無效的音量格式。請使用例如: 1.5、150%、+6dB、-3dB、0.8x", err=True)
                return False

            if expr:
                # 將濾鏡套用到後處理階段
                ydl_opts['postprocessor_args'] = ['-filter:a', expr]
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                click.echo("🚀 開始下載並轉換為 MP3...")
                ydl.download([url])
            
            click.echo("✅ MP3 下載完成！")
            return True
            
        except Exception as e:
            click.echo(f"❌ MP3 下載失敗: {e}", err=True)
            return False
    
    def _get_video_format_selector(self, quality: str) -> str:
        """根據畫質選擇器返回適當的格式選擇器."""
        quality_map = {
            "best": "best[ext=mp4]/best",
            "1080p": "best[height<=1080][ext=mp4]/best[height<=1080]",
            "720p": "best[height<=720][ext=mp4]/best[height<=720]",
            "480p": "best[height<=480][ext=mp4]/best[height<=480]",
            "360p": "best[height<=360][ext=mp4]/best[height<=360]",
            "worst": "worst[ext=mp4]/worst",
        }
        return quality_map.get(quality, "best[ext=mp4]/best")
    
    def _progress_hook(self, d):
        """下載進度回調."""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                click.echo(f"\r📥 下載進度: {percent:.1f}%", nl=False)
        elif d['status'] == 'finished':
            click.echo("\n🔄 處理完成...")


@click.group()
@click.version_option(version='0.3.0')
def cli():
    """
    YouTube 下載器 - 支援影片 (MP4) 和音訊 (MP3) 下載
    
    使用範例:
        python -m youtube_transfer.cli video "https://www.youtube.com/watch?v=VIDEO_ID"
        python -m youtube_transfer.cli audio "https://www.youtube.com/watch?v=VIDEO_ID"
    """
    pass


@cli.command()
@click.argument('url', required=True)
@click.option('--output-dir', '-o', default='downloads', 
              help='輸出目錄 (預設: downloads)')
@click.option('--quality', '-q', 
              type=click.Choice(['best', '1080p', '720p', '480p', '360p', 'worst']),
              default='best',
              help='影片畫質 (預設: best)')
def video(url: str, output_dir: str, quality: str):
    """下載 YouTube 影片為 MP4 格式."""
    click.echo("🎬 YouTube 影片下載器")
    click.echo("=" * 40)
    
    # 建立轉換器
    converter = YouTubeConverter(output_dir)
    
    # 開始下載
    success = converter.download_video(url, quality)
    
    if success:
        click.echo(f"📁 影片已儲存至: {output_dir}")
    else:
        sys.exit(1)


@cli.command()
@click.argument('url', required=True)
@click.option('--output-dir', '-o', default='downloads', 
              help='輸出目錄 (預設: downloads)')
@click.option('--quality', '-q', default='192', 
              help='MP3 音質 (預設: 192)')
@click.option('--volume', default=None, help='調整音量，例如: 1.5、150%、+6dB、-3dB、0.8x')
def audio(url: str, output_dir: str, quality: str, volume: Optional[str]):
    """下載 YouTube 影片並轉換為 MP3 格式."""
    click.echo("🎵 YouTube 轉 MP3 下載器")
    click.echo("=" * 40)
    
    # 檢查 FFmpeg
    if not _check_ffmpeg():
        click.echo("❌ 需要安裝 FFmpeg 才能轉換音訊格式", err=True)
        click.echo("請安裝 FFmpeg: https://ffmpeg.org/download.html", err=True)
        sys.exit(1)
    
    # 建立轉換器
    converter = YouTubeConverter(output_dir)
    
    # 開始下載
    success = converter.download_audio(url, quality, volume)
    
    if success:
        click.echo(f"📁 MP3 檔案已儲存至: {output_dir}")
    else:
        sys.exit(1)


@cli.command()
@click.argument('url', required=True)
def info(url: str):
    """顯示影片資訊和可用格式."""
    click.echo("ℹ️  影片資訊")
    click.echo("=" * 40)
    
    converter = YouTubeConverter()
    
    if not converter.validate_youtube_url(url):
        click.echo("❌ 無效的 YouTube URL", err=True)
        sys.exit(1)
    
    # 獲取基本資訊
    info = converter.get_video_info(url)
    if not info:
        sys.exit(1)
    
    click.echo(f"📹 標題: {info['title']}")
    click.echo(f"👤 上傳者: {info['uploader']}")
    if info['duration']:
        minutes = info['duration'] // 60
        seconds = info['duration'] % 60
        click.echo(f"⏱️  時長: {minutes}:{seconds:02d}")
    
    # 獲取可用格式
    formats = converter.get_available_formats(url)
    
    click.echo("\n📺 可用影片格式:")
    for fmt in formats['video'][:5]:  # 只顯示前5個
        height = fmt.get('height', 'Unknown')
        ext = fmt.get('ext', 'Unknown')
        click.echo(f"  - {height}p ({ext}) - {fmt.get('format_note', '')}")
    
    click.echo("\n🎵 可用音訊格式:")
    for fmt in formats['audio'][:3]:  # 只顯示前3個
        abr = fmt.get('abr', 'Unknown')
        ext = fmt.get('ext', 'Unknown')
        click.echo(f"  - {abr}kbps ({ext}) - {fmt.get('format_note', '')}")


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


# 為了向後相容，保留舊的 main 函數
def main():
    """向後相容的主函數，預設為音訊下載."""
    # 檢查是否有子命令
    if len(sys.argv) > 1 and sys.argv[1] in ['video', 'audio', 'info']:
        # 有子命令，直接執行
        cli()
    else:
        # 沒有子命令，預設為音訊下載
        if len(sys.argv) > 1:
            # 有 URL 參數，插入 audio 子命令
            sys.argv.insert(1, 'audio')
        else:
            # 沒有參數，顯示幫助
            pass
        cli()


if __name__ == '__main__':
    main() 