# YouTube 视频摘要工具

一个强大的 YouTube 视频知识提取工具，帮助你快速吸收视频内容。

## 功能特点

- **收藏管理**: 轻松保存想看的 YouTube 视频链接
- **字幕下载**: 自动下载多语言字幕（支持中文、英文等）
- **AI 摘要**: 使用 Claude/GPT 生成结构化摘要
- **智能分类**: 自动识别视频分类和标签
- **快速搜索**: 按标题、分类、标签搜索视频
- **知识管理**: 统计分析你的学习内容

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API 密钥

复制 `.env.example` 为 `.env`，并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# 推荐使用 Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 或使用 OpenAI
# OPENAI_API_KEY=your_openai_api_key_here
```

**获取 API 密钥**：
- Anthropic Claude: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys

### 3. 开始使用

#### 一键处理视频（推荐）

```bash
python main.py process "https://www.youtube.com/watch?v=xxxxx"
```

这会自动完成：添加视频 → 下载字幕 → 生成摘要

#### 分步操作

```bash
# 1. 添加视频
python main.py add "https://www.youtube.com/watch?v=xxxxx"

# 2. 下载字幕（会显示视频ID）
python main.py download <video_id>

# 3. 生成摘要
python main.py summarize <video_id>
```

## 使用示例

### 列出所有视频

```bash
python main.py list
```

输出示例：
```
共 5 个视频:

1. ✅ [abc123]
   标题: 深度学习入门教程
   频道: AI 学习频道
   分类: 技术/编程, 教育/学习
   标签: 深度学习, 机器学习, Python
   摘要: 本视频介绍了深度学习的基本概念...

2. 📄 [def456]
   标题: 创业思维与商业模式
   频道: 创业智库
   ...
```

### 查看视频详情

```bash
python main.py show <video_id>
```

### 搜索视频

```bash
python main.py search "机器学习"
```

### 查看统计信息

```bash
python main.py stats
```

输出示例：
```
📊 统计信息
============================================================
总视频数: 15
已生成摘要: 12
已下载字幕: 14

【分类统计】
  技术/编程: 8
  教育/学习: 5
  商业/创业: 2

【热门标签】
  机器学习: 6
  Python: 5
  深度学习: 4
```

## 命令详解

### process - 一键处理（推荐）

```bash
python main.py process <YouTube_URL> [--lang LANG]
```

参数：
- `<YouTube_URL>`: YouTube 视频 URL
- `--lang`: 字幕语言（默认: zh-Hans）

支持的语言代码：
- `zh-Hans`: 简体中文
- `zh-Hant`: 繁体中文
- `en`: 英文
- `ja`: 日文
- `ko`: 韩文

### add - 添加视频

```bash
python main.py add <YouTube_URL>
```

### download - 下载字幕

```bash
python main.py download <video_id> [--lang LANG]
```

### summarize - 生成摘要

```bash
python main.py summarize <video_id>
```

生成的摘要包含：
- **核心摘要**: 2-3 句话快速概括
- **关键要点**: 3-5 个核心观点
- **详细摘要**: 200-300 字深度总结
- **分类**: 自动识别内容类型
- **标签**: 相关主题标签
- **适合人群**: 目标受众
- **知识难度**: 初级/中级/高级

### list - 列出视频

```bash
python main.py list [--status STATUS]
```

状态筛选：
- `added`: 已添加
- `downloaded`: 已下载字幕
- `summarized`: 已生成摘要

### show - 查看详情

```bash
python main.py show <video_id>
```

### search - 搜索

```bash
python main.py search <关键词>
```

在标题、描述、标签、分类中搜索

### stats - 统计信息

```bash
python main.py stats
```

## 项目结构

```
youtube-summarizer/
├── src/
│   ├── __init__.py
│   ├── downloader.py    # YouTube 字幕下载器
│   ├── summarizer.py    # AI 摘要生成器
│   ├── storage.py       # 数据存储管理
│   └── cli.py           # 命令行界面
├── data/
│   └── videos.json      # 视频数据存储
├── main.py              # 程序入口
├── requirements.txt     # 依赖包
├── .env.example         # 环境变量示例
├── .gitignore
└── README.md
```

## 工作流程

```
添加视频 → 下载字幕 → AI 分析 → 生成摘要 → 自动分类
   ↓          ↓          ↓          ↓          ↓
 获取信息   多语言支持   深度理解   结构化输出   智能标签
```

## 典型使用场景

### 学习管理

```bash
# 收藏一系列教程视频
python main.py add "https://youtube.com/watch?v=tutorial1"
python main.py add "https://youtube.com/watch?v=tutorial2"

# 批量下载字幕
python main.py list --status added | grep -o '\[.*\]' | while read id; do
    python main.py download ${id//[\[\]]/}
done

# 查看学习统计
python main.py stats
```

### 快速筛选

```bash
# 搜索特定主题
python main.py search "Python"

# 查看摘要决定是否观看
python main.py show <video_id>
```

## 数据存储

所有数据存储在 `data/videos.json`，包括：
- 视频基本信息
- 字幕内容
- AI 生成的摘要
- 分类和标签
- 个人笔记

数据格式为 JSON，方便备份和迁移。

## 依赖说明

- **yt-dlp**: YouTube 视频信息和字幕下载
- **anthropic**: Anthropic Claude API 客户端
- **openai**: OpenAI GPT API 客户端
- **requests**: HTTP 请求库
- **python-dateutil**: 日期处理

## 常见问题

### Q: 如何获取 video_id？

A: 运行 `python main.py list` 会显示所有视频的 ID（在方括号中）

### Q: 支持哪些 YouTube URL 格式？

A: 支持以下格式：
- https://www.youtube.com/watch?v=xxxxx
- https://youtu.be/xxxxx
- https://www.youtube.com/embed/xxxxx

### Q: 如果视频没有字幕怎么办？

A: 工具会尝试下载自动生成的字幕。运行 `python main.py download <video_id>` 会显示可用的字幕语言。

### Q: API 费用如何？

A:
- Anthropic Claude: 每个摘要约 $0.01-0.03
- OpenAI GPT-4: 每个摘要约 $0.02-0.05

### Q: 可以离线使用吗？

A: 下载字幕后可以离线查看，但生成摘要需要联网调用 AI API。

## 高级功能

### 自定义 AI 提示词

编辑 `src/summarizer.py` 中的 `prompt` 变量来自定义摘要风格。

### 批量处理

创建脚本批量处理多个视频：

```bash
#!/bin/bash
urls=(
    "https://youtube.com/watch?v=xxx1"
    "https://youtube.com/watch?v=xxx2"
    "https://youtube.com/watch?v=xxx3"
)

for url in "${urls[@]}"; do
    python main.py process "$url"
    sleep 5  # 避免 API 限流
done
```

## 未来计划

- [ ] Web 界面
- [ ] 导出功能（Markdown, PDF）
- [ ] 笔记功能
- [ ] 观看进度跟踪
- [ ] 播放列表批量导入
- [ ] 视频推荐
- [ ] 多用户支持

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 下载工具
- [Anthropic Claude](https://www.anthropic.com/) - AI 摘要生成
- [OpenAI](https://openai.com/) - AI 摘要生成

---

**提示**: 首次使用建议先用 `process` 命令处理一个短视频测试功能是否正常。

祝你学习愉快！
