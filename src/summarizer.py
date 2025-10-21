"""AI 摘要生成模块"""

import os
from typing import Dict, Optional, List
from anthropic import Anthropic


class VideoSummarizer:
    """使用 AI 生成视频摘要和分类"""

    def __init__(self, api_key: Optional[str] = None, provider: str = 'anthropic'):
        """初始化摘要生成器

        Args:
            api_key: API 密钥，如果不提供则从环境变量读取
            provider: AI 提供商，'anthropic' 或 'openai'
        """
        self.provider = provider

        if provider == 'anthropic':
            self.client = Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
            self.model = "claude-3-5-sonnet-20241022"
        elif provider == 'openai':
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
            self.model = "gpt-4-turbo-preview"
        else:
            raise ValueError(f"不支持的 AI 提供商: {provider}")

    def generate_summary(self, transcript: str, video_info: Dict) -> Dict:
        """生成视频摘要、关键要点和分类

        Args:
            transcript: 视频字幕文本
            video_info: 视频基本信息

        Returns:
            包含摘要、关键要点、分类和标签的字典
        """
        title = video_info.get('title', '未知标题')

        prompt = f"""请分析以下 YouTube 视频的字幕内容，并提供详细的摘要。

视频标题：{title}

字幕内容：
{transcript[:8000]}

请按以下格式提供分析（使用中文）：

## 核心摘要
（2-3 句话概括视频主要内容）

## 关键要点
- 要点 1
- 要点 2
- 要点 3
（列出 3-5 个关键要点）

## 详细摘要
（200-300 字的详细摘要）

## 分类
（选择最合适的 1-2 个分类：技术/编程、商业/创业、教育/学习、科学、娱乐、生活方式、新闻/时事、其他）

## 推荐标签
（3-5 个相关标签，用逗号分隔）

## 适合人群
（这个视频最适合哪些人观看）

## 知识难度
（初级/中级/高级）
"""

        try:
            if self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                summary_text = response.content[0].text
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000
                )
                summary_text = response.choices[0].message.content

            # 解析返回的结构化摘要
            return self._parse_summary(summary_text)

        except Exception as e:
            raise Exception(f"生成摘要失败: {str(e)}")

    def _parse_summary(self, summary_text: str) -> Dict:
        """解析 AI 返回的摘要文本为结构化数据"""
        sections = {}
        current_section = None
        current_content = []

        for line in summary_text.split('\n'):
            line = line.strip()

            # 检测章节标题
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif line and current_section:
                current_content.append(line)

        # 保存最后一个章节
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        # 提取关键信息
        key_points = []
        if '关键要点' in sections:
            for line in sections['关键要点'].split('\n'):
                if line.strip().startswith('-'):
                    key_points.append(line.strip()[1:].strip())

        # 提取分类
        categories = []
        if '分类' in sections:
            categories = [c.strip() for c in sections['分类'].replace('、', ',').split(',')]

        # 提取标签
        tags = []
        if '推荐标签' in sections:
            tags = [t.strip() for t in sections['推荐标签'].replace('、', ',').split(',')]

        return {
            'core_summary': sections.get('核心摘要', ''),
            'key_points': key_points,
            'detailed_summary': sections.get('详细摘要', ''),
            'categories': categories,
            'tags': tags,
            'target_audience': sections.get('适合人群', ''),
            'difficulty': sections.get('知识难度', ''),
            'full_text': summary_text
        }

    def quick_summary(self, transcript: str, max_length: int = 200) -> str:
        """生成简短摘要（快速模式）

        Args:
            transcript: 字幕文本
            max_length: 最大字数

        Returns:
            简短摘要文本
        """
        prompt = f"""请用 {max_length} 字以内简要概括以下内容的核心要点：

{transcript[:5000]}

只需要返回摘要文本，不需要其他格式。
"""

        try:
            if self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text.strip()
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"生成快速摘要失败: {str(e)}")
