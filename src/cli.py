"""命令行界面模块"""

import argparse
import sys
from typing import Optional
from .downloader import YouTubeDownloader
from .summarizer import VideoSummarizer
from .storage import VideoStorage


class CLI:
    """YouTube 摘要工具命令行界面"""

    def __init__(self):
        self.downloader = YouTubeDownloader()
        self.storage = VideoStorage()
        self.summarizer = None  # 懒加载

    def _init_summarizer(self):
        """懒加载 AI 摘要器"""
        if self.summarizer is None:
            try:
                self.summarizer = VideoSummarizer()
            except Exception as e:
                print(f"警告: AI 摘要功能初始化失败: {e}")
                print("请确保设置了 ANTHROPIC_API_KEY 或 OPENAI_API_KEY 环境变量")
                return False
        return True

    def add_video(self, url: str):
        """添加视频到收藏"""
        print(f"正在获取视频信息: {url}")

        try:
            video_info = self.downloader.get_video_info(url)
            video_id = self.storage.add_video(url, video_info)

            print(f"\n✓ 视频已添加到收藏")
            print(f"  标题: {video_info['title']}")
            print(f"  频道: {video_info['channel']}")
            print(f"  时长: {video_info['duration']} 秒")
            print(f"  ID: {video_id}")

            # 检查可用字幕
            langs = self.downloader.get_available_subtitles(url)
            if langs:
                print(f"  可用字幕: {', '.join(langs[:5])}")

            return video_id

        except Exception as e:
            print(f"✗ 添加失败: {e}")
            sys.exit(1)

    def download_transcript(self, video_id: str, lang: str = 'zh-Hans'):
        """下载视频字幕"""
        video = self.storage.get_video(video_id)
        if not video:
            print(f"✗ 视频不存在: {video_id}")
            return

        print(f"正在下载字幕: {video['title']}")

        try:
            transcript = self.downloader.download_subtitles(video['url'], lang)

            if transcript:
                self.storage.update_video(video_id, {
                    'transcript': transcript,
                    'status': 'downloaded'
                })
                print(f"✓ 字幕下载成功 ({len(transcript)} 字符)")
            else:
                print(f"✗ 未找到 {lang} 字幕，请尝试其他语言")
                langs = self.downloader.get_available_subtitles(video['url'])
                if langs:
                    print(f"  可用字幕: {', '.join(langs)}")

        except Exception as e:
            print(f"✗ 下载失败: {e}")

    def summarize_video(self, video_id: str):
        """生成视频摘要"""
        if not self._init_summarizer():
            return

        video = self.storage.get_video(video_id)
        if not video:
            print(f"✗ 视频不存在: {video_id}")
            return

        if not video.get('transcript'):
            print("✗ 请先下载字幕")
            return

        print(f"正在生成摘要: {video['title']}")
        print("这可能需要几秒钟...")

        try:
            summary = self.summarizer.generate_summary(
                video['transcript'],
                video
            )

            # 保存摘要
            self.storage.update_video(video_id, {
                'summary': summary,
                'status': 'summarized'
            })

            # 自动添加分类和标签
            if summary.get('categories'):
                self.storage.add_categories(video_id, summary['categories'])
            if summary.get('tags'):
                self.storage.add_tags(video_id, summary['tags'])

            # 显示摘要
            self._display_summary(video, summary)

        except Exception as e:
            print(f"✗ 生成摘要失败: {e}")

    def _display_summary(self, video: dict, summary: dict):
        """显示摘要信息"""
        print("\n" + "="*60)
        print(f"📺 {video['title']}")
        print("="*60)

        if summary.get('core_summary'):
            print(f"\n【核心摘要】")
            print(summary['core_summary'])

        if summary.get('key_points'):
            print(f"\n【关键要点】")
            for i, point in enumerate(summary['key_points'], 1):
                print(f"  {i}. {point}")

        if summary.get('detailed_summary'):
            print(f"\n【详细摘要】")
            print(summary['detailed_summary'])

        if summary.get('categories'):
            print(f"\n【分类】{', '.join(summary['categories'])}")

        if summary.get('tags'):
            print(f"【标签】{', '.join(summary['tags'])}")

        if summary.get('target_audience'):
            print(f"【适合人群】{summary['target_audience']}")

        if summary.get('difficulty'):
            print(f"【难度等级】{summary['difficulty']}")

        print("="*60)

    def list_videos(self, status: Optional[str] = None):
        """列出所有视频"""
        videos = self.storage.get_all_videos()

        if status:
            videos = [v for v in videos if v.get('status') == status]

        if not videos:
            print("还没有收藏任何视频")
            return

        print(f"\n共 {len(videos)} 个视频:\n")

        for i, video in enumerate(videos, 1):
            status_icon = {
                'added': '📥',
                'downloaded': '📄',
                'summarized': '✅'
            }.get(video.get('status', 'added'), '📥')

            print(f"{i}. {status_icon} [{video['video_id']}]")
            print(f"   标题: {video['title']}")
            print(f"   频道: {video.get('channel', 'N/A')}")

            if video.get('categories'):
                print(f"   分类: {', '.join(video['categories'])}")

            if video.get('tags'):
                print(f"   标签: {', '.join(video['tags'][:5])}")

            if video.get('summary', {}).get('core_summary'):
                summary = video['summary']['core_summary']
                print(f"   摘要: {summary[:100]}...")

            print()

    def show_video(self, video_id: str):
        """显示视频详细信息"""
        video = self.storage.get_video(video_id)
        if not video:
            print(f"✗ 视频不存在: {video_id}")
            return

        print("\n" + "="*60)
        print(f"📺 {video['title']}")
        print("="*60)
        print(f"频道: {video.get('channel', 'N/A')}")
        print(f"时长: {video.get('duration', 'N/A')} 秒")
        print(f"上传日期: {video.get('upload_date', 'N/A')}")
        print(f"观看次数: {video.get('view_count', 'N/A')}")
        print(f"URL: {video['url']}")
        print(f"状态: {video.get('status', 'added')}")

        if video.get('categories'):
            print(f"分类: {', '.join(video['categories'])}")

        if video.get('tags'):
            print(f"标签: {', '.join(video['tags'])}")

        if video.get('summary'):
            print("\n")
            self._display_summary(video, video['summary'])
        else:
            print("\n尚未生成摘要")

    def search(self, query: str):
        """搜索视频"""
        results = self.storage.search_videos(query)

        if not results:
            print(f"未找到匹配 '{query}' 的视频")
            return

        print(f"\n找到 {len(results)} 个匹配的视频:\n")

        for i, video in enumerate(results, 1):
            print(f"{i}. [{video['video_id']}] {video['title']}")
            if video.get('categories'):
                print(f"   分类: {', '.join(video['categories'])}")
            print()

    def statistics(self):
        """显示统计信息"""
        stats = self.storage.get_statistics()

        print("\n" + "="*60)
        print("📊 统计信息")
        print("="*60)
        print(f"总视频数: {stats['total_videos']}")
        print(f"已生成摘要: {stats['summarized']}")
        print(f"已下载字幕: {stats['with_transcript']}")

        if stats['categories']:
            print(f"\n【分类统计】")
            for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count}")

        if stats['tags']:
            print(f"\n【热门标签】")
            top_tags = sorted(stats['tags'].items(), key=lambda x: x[1], reverse=True)[:10]
            for tag, count in top_tags:
                print(f"  {tag}: {count}")

        print("="*60)

    def process_video(self, url: str, lang: str = 'zh-Hans'):
        """一键处理视频（添加、下载字幕、生成摘要）"""
        print(f"开始处理视频: {url}\n")

        # 添加视频
        video_id = self.add_video(url)

        # 下载字幕
        print()
        self.download_transcript(video_id, lang)

        # 生成摘要
        print()
        self.summarize_video(video_id)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='YouTube 视频摘要工具 - 快速吸收视频知识',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 一键处理视频（添加+下载+摘要）
  python main.py process https://www.youtube.com/watch?v=xxxxx

  # 添加视频到收藏
  python main.py add https://www.youtube.com/watch?v=xxxxx

  # 下载字幕
  python main.py download <video_id>

  # 生成摘要
  python main.py summarize <video_id>

  # 列出所有视频
  python main.py list

  # 搜索视频
  python main.py search "机器学习"

  # 查看统计
  python main.py stats
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # process 命令（一键处理）
    process_parser = subparsers.add_parser('process', help='一键处理视频（推荐）')
    process_parser.add_argument('url', help='YouTube 视频 URL')
    process_parser.add_argument('--lang', default='zh-Hans', help='字幕语言 (默认: zh-Hans)')

    # add 命令
    add_parser = subparsers.add_parser('add', help='添加视频到收藏')
    add_parser.add_argument('url', help='YouTube 视频 URL')

    # download 命令
    download_parser = subparsers.add_parser('download', help='下载视频字幕')
    download_parser.add_argument('video_id', help='视频 ID')
    download_parser.add_argument('--lang', default='zh-Hans', help='字幕语言 (默认: zh-Hans)')

    # summarize 命令
    summarize_parser = subparsers.add_parser('summarize', help='生成视频摘要')
    summarize_parser.add_argument('video_id', help='视频 ID')

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有视频')
    list_parser.add_argument('--status', choices=['added', 'downloaded', 'summarized'],
                            help='按状态筛选')

    # show 命令
    show_parser = subparsers.add_parser('show', help='显示视频详情')
    show_parser.add_argument('video_id', help='视频 ID')

    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索视频')
    search_parser.add_argument('query', help='搜索关键词')

    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = CLI()

    # 执行命令
    if args.command == 'process':
        cli.process_video(args.url, args.lang)
    elif args.command == 'add':
        cli.add_video(args.url)
    elif args.command == 'download':
        cli.download_transcript(args.video_id, args.lang)
    elif args.command == 'summarize':
        cli.summarize_video(args.video_id)
    elif args.command == 'list':
        cli.list_videos(args.status)
    elif args.command == 'show':
        cli.show_video(args.video_id)
    elif args.command == 'search':
        cli.search(args.query)
    elif args.command == 'stats':
        cli.statistics()


if __name__ == '__main__':
    main()
