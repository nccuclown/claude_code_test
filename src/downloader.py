"""YouTube 字幕下载模块"""

import yt_dlp
import re
from typing import Dict, Optional, List


class YouTubeDownloader:
    """YouTube 视频信息和字幕下载器"""

    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }

    def extract_video_id(self, url: str) -> Optional[str]:
        """从 YouTube URL 提取视频 ID"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]*)',
            r'youtube\.com\/embed\/([^&\n?]*)',
            r'youtube\.com\/v\/([^&\n?]*)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_info(self, url: str) -> Dict:
        """获取视频基本信息"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                return {
                    'video_id': info.get('id'),
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'channel': info.get('channel'),
                    'thumbnail': info.get('thumbnail'),
                }
        except Exception as e:
            raise Exception(f"获取视频信息失败: {str(e)}")

    def download_subtitles(self, url: str, lang: str = 'zh-Hans') -> Optional[str]:
        """下载视频字幕

        Args:
            url: YouTube 视频 URL
            lang: 字幕语言代码，默认为中文简体 (zh-Hans)
                  其他选项: 'en' (英文), 'zh-Hant' (繁体中文), 'ja' (日文) 等

        Returns:
            字幕文本内容，如果没有字幕则返回 None
        """
        subtitle_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang, 'en'],  # 优先下载指定语言，后备英文
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # 尝试获取字幕
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})

                # 优先使用手动字幕，其次自动生成字幕
                all_subs = {**automatic_captions, **subtitles}

                # 尝试获取指定语言的字幕
                for lang_code in [lang, 'en', 'zh-Hant']:
                    if lang_code in all_subs:
                        sub_info = all_subs[lang_code]
                        # 找到文本格式的字幕
                        for sub in sub_info:
                            if sub.get('ext') in ['json3', 'srv3', 'srv2', 'srv1']:
                                # 下载字幕内容
                                sub_url = sub.get('url')
                                if sub_url:
                                    return self._download_subtitle_content(sub_url)

                return None

        except Exception as e:
            raise Exception(f"下载字幕失败: {str(e)}")

    def _download_subtitle_content(self, url: str) -> str:
        """从 URL 下载字幕内容并解析"""
        import requests
        import json

        try:
            response = requests.get(url)
            response.raise_for_status()

            # 解析 YouTube 字幕 JSON 格式
            data = json.loads(response.text)

            if 'events' in data:
                # JSON3 格式
                texts = []
                for event in data['events']:
                    if 'segs' in event:
                        for seg in event['segs']:
                            if 'utf8' in seg:
                                texts.append(seg['utf8'])
                return ' '.join(texts)

            return response.text

        except Exception as e:
            raise Exception(f"解析字幕内容失败: {str(e)}")

    def get_available_subtitles(self, url: str) -> List[str]:
        """获取视频可用的字幕语言列表"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})

                all_langs = set(list(subtitles.keys()) + list(automatic_captions.keys()))
                return sorted(list(all_langs))

        except Exception as e:
            raise Exception(f"获取字幕语言列表失败: {str(e)}")
