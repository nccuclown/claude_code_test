"""数据存储管理模块"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class VideoStorage:
    """视频数据存储管理器"""

    def __init__(self, data_file: str = 'data/videos.json'):
        """初始化存储管理器

        Args:
            data_file: 数据文件路径
        """
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # 如果文件不存在，创建空数据文件
        if not self.data_file.exists():
            self._save_data({'videos': []})

    def _load_data(self) -> Dict:
        """加载数据文件"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据失败: {e}")
            return {'videos': []}

    def _save_data(self, data: Dict):
        """保存数据到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"保存数据失败: {e}")

    def add_video(self, url: str, video_info: Dict) -> str:
        """添加新视频

        Args:
            url: 视频 URL
            video_info: 视频信息

        Returns:
            视频 ID
        """
        data = self._load_data()

        video_id = video_info.get('video_id')

        # 检查是否已存在
        for video in data['videos']:
            if video.get('video_id') == video_id:
                print(f"视频已存在: {video.get('title')}")
                return video_id

        # 添加新视频
        video_entry = {
            'video_id': video_id,
            'url': url,
            'title': video_info.get('title'),
            'description': video_info.get('description'),
            'duration': video_info.get('duration'),
            'uploader': video_info.get('uploader'),
            'channel': video_info.get('channel'),
            'upload_date': video_info.get('upload_date'),
            'view_count': video_info.get('view_count'),
            'thumbnail': video_info.get('thumbnail'),
            'added_date': datetime.now().isoformat(),
            'transcript': None,
            'summary': None,
            'tags': [],
            'categories': [],
            'notes': '',
            'status': 'added',  # added, downloaded, summarized
        }

        data['videos'].append(video_entry)
        self._save_data(data)

        return video_id

    def update_video(self, video_id: str, updates: Dict):
        """更新视频信息

        Args:
            video_id: 视频 ID
            updates: 要更新的字段
        """
        data = self._load_data()

        for video in data['videos']:
            if video.get('video_id') == video_id:
                video.update(updates)
                self._save_data(data)
                return

        raise ValueError(f"视频不存在: {video_id}")

    def get_video(self, video_id: str) -> Optional[Dict]:
        """获取视频信息

        Args:
            video_id: 视频 ID

        Returns:
            视频信息字典，如果不存在则返回 None
        """
        data = self._load_data()

        for video in data['videos']:
            if video.get('video_id') == video_id:
                return video

        return None

    def get_all_videos(self) -> List[Dict]:
        """获取所有视频"""
        data = self._load_data()
        return data.get('videos', [])

    def search_videos(self, query: str) -> List[Dict]:
        """搜索视频

        Args:
            query: 搜索关键词

        Returns:
            匹配的视频列表
        """
        data = self._load_data()
        results = []
        query_lower = query.lower()

        for video in data['videos']:
            # 在标题、描述、标签中搜索
            if (query_lower in video.get('title', '').lower() or
                query_lower in video.get('description', '').lower() or
                any(query_lower in tag.lower() for tag in video.get('tags', [])) or
                any(query_lower in cat.lower() for cat in video.get('categories', []))):
                results.append(video)

        return results

    def filter_by_category(self, category: str) -> List[Dict]:
        """按分类筛选视频

        Args:
            category: 分类名称

        Returns:
            该分类的所有视频
        """
        data = self._load_data()
        results = []

        for video in data['videos']:
            if category in video.get('categories', []):
                results.append(video)

        return results

    def filter_by_tag(self, tag: str) -> List[Dict]:
        """按标签筛选视频

        Args:
            tag: 标签名称

        Returns:
            该标签的所有视频
        """
        data = self._load_data()
        results = []

        for video in data['videos']:
            if tag in video.get('tags', []):
                results.append(video)

        return results

    def add_tags(self, video_id: str, tags: List[str]):
        """添加标签

        Args:
            video_id: 视频 ID
            tags: 标签列表
        """
        video = self.get_video(video_id)
        if video:
            current_tags = set(video.get('tags', []))
            current_tags.update(tags)
            self.update_video(video_id, {'tags': list(current_tags)})

    def add_categories(self, video_id: str, categories: List[str]):
        """添加分类

        Args:
            video_id: 视频 ID
            categories: 分类列表
        """
        video = self.get_video(video_id)
        if video:
            current_cats = set(video.get('categories', []))
            current_cats.update(categories)
            self.update_video(video_id, {'categories': list(current_cats)})

    def delete_video(self, video_id: str):
        """删除视频

        Args:
            video_id: 视频 ID
        """
        data = self._load_data()
        data['videos'] = [v for v in data['videos'] if v.get('video_id') != video_id]
        self._save_data(data)

    def get_statistics(self) -> Dict:
        """获取统计信息

        Returns:
            统计信息字典
        """
        videos = self.get_all_videos()

        stats = {
            'total_videos': len(videos),
            'summarized': sum(1 for v in videos if v.get('summary')),
            'with_transcript': sum(1 for v in videos if v.get('transcript')),
            'categories': {},
            'tags': {},
        }

        # 统计分类和标签
        for video in videos:
            for cat in video.get('categories', []):
                stats['categories'][cat] = stats['categories'].get(cat, 0) + 1

            for tag in video.get('tags', []):
                stats['tags'][tag] = stats['tags'].get(tag, 0) + 1

        return stats
