"""FastAPI 后端应用"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.downloader import YouTubeDownloader
from src.summarizer import VideoSummarizer
from src.storage import VideoStorage

app = FastAPI(title="YouTube 视频摘要工具", version="1.0.0")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 模板引擎
templates = Jinja2Templates(directory="web/templates")

# 初始化核心组件
downloader = YouTubeDownloader()
storage = VideoStorage()
summarizer = None  # 懒加载


# ==================== 数据模型 ====================

class VideoAddRequest(BaseModel):
    url: str


class VideoProcessRequest(BaseModel):
    url: str
    lang: str = "zh-Hans"


class VideoSummarizeRequest(BaseModel):
    video_id: str


class VideoDownloadRequest(BaseModel):
    video_id: str
    lang: str = "zh-Hans"


class VideoSearchRequest(BaseModel):
    query: str


# ==================== 页面路由 ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/videos", response_class=HTMLResponse)
async def videos_page(request: Request):
    """视频列表页"""
    return templates.TemplateResponse("videos.html", {"request": request})


@app.get("/video/{video_id}", response_class=HTMLResponse)
async def video_detail_page(request: Request, video_id: str):
    """视频详情页"""
    return templates.TemplateResponse("video_detail.html", {
        "request": request,
        "video_id": video_id
    })


@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    """统计页面"""
    return templates.TemplateResponse("stats.html", {"request": request})


# ==================== API 端点 ====================

@app.get("/api/videos")
async def get_videos(status: Optional[str] = None):
    """获取所有视频列表"""
    videos = storage.get_all_videos()

    if status:
        videos = [v for v in videos if v.get('status') == status]

    return {
        "success": True,
        "data": videos,
        "total": len(videos)
    }


@app.get("/api/video/{video_id}")
async def get_video(video_id: str):
    """获取单个视频详情"""
    video = storage.get_video(video_id)

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    return {
        "success": True,
        "data": video
    }


@app.post("/api/video/add")
async def add_video(request: VideoAddRequest):
    """添加视频"""
    try:
        video_info = downloader.get_video_info(request.url)
        video_id = storage.add_video(request.url, video_info)

        # 获取可用字幕
        langs = downloader.get_available_subtitles(request.url)

        return {
            "success": True,
            "message": "视频添加成功",
            "data": {
                "video_id": video_id,
                "title": video_info.get('title'),
                "available_langs": langs
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/video/download")
async def download_transcript(request: VideoDownloadRequest):
    """下载视频字幕"""
    try:
        video = storage.get_video(request.video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")

        transcript = downloader.download_subtitles(video['url'], request.lang)

        if not transcript:
            raise HTTPException(status_code=400, detail=f"未找到 {request.lang} 字幕")

        storage.update_video(request.video_id, {
            'transcript': transcript,
            'status': 'downloaded'
        })

        return {
            "success": True,
            "message": "字幕下载成功",
            "data": {
                "transcript_length": len(transcript)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/video/summarize")
async def summarize_video(request: VideoSummarizeRequest):
    """生成视频摘要"""
    global summarizer

    try:
        # 懒加载 AI 摘要器
        if summarizer is None:
            summarizer = VideoSummarizer()

        video = storage.get_video(request.video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")

        if not video.get('transcript'):
            raise HTTPException(status_code=400, detail="请先下载字幕")

        # 生成摘要
        summary = summarizer.generate_summary(video['transcript'], video)

        # 保存摘要
        storage.update_video(request.video_id, {
            'summary': summary,
            'status': 'summarized'
        })

        # 自动添加分类和标签
        if summary.get('categories'):
            storage.add_categories(request.video_id, summary['categories'])
        if summary.get('tags'):
            storage.add_tags(request.video_id, summary['tags'])

        return {
            "success": True,
            "message": "摘要生成成功",
            "data": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/video/process")
async def process_video(request: VideoProcessRequest, background_tasks: BackgroundTasks):
    """一键处理视频（添加+下载+摘要）"""
    try:
        # 1. 添加视频
        video_info = downloader.get_video_info(request.url)
        video_id = storage.add_video(request.url, video_info)

        # 2. 下载字幕
        transcript = downloader.download_subtitles(request.url, request.lang)
        if not transcript:
            raise HTTPException(status_code=400, detail=f"未找到 {request.lang} 字幕")

        storage.update_video(video_id, {
            'transcript': transcript,
            'status': 'downloaded'
        })

        # 3. 生成摘要
        global summarizer
        if summarizer is None:
            summarizer = VideoSummarizer()

        summary = summarizer.generate_summary(transcript, video_info)

        storage.update_video(video_id, {
            'summary': summary,
            'status': 'summarized'
        })

        # 自动添加分类和标签
        if summary.get('categories'):
            storage.add_categories(video_id, summary['categories'])
        if summary.get('tags'):
            storage.add_tags(video_id, summary['tags'])

        # 获取完整视频信息
        video = storage.get_video(video_id)

        return {
            "success": True,
            "message": "视频处理成功",
            "data": video
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/video/search")
async def search_videos(request: VideoSearchRequest):
    """搜索视频"""
    results = storage.search_videos(request.query)

    return {
        "success": True,
        "data": results,
        "total": len(results)
    }


@app.get("/api/stats")
async def get_statistics():
    """获取统计信息"""
    stats = storage.get_statistics()

    return {
        "success": True,
        "data": stats
    }


@app.delete("/api/video/{video_id}")
async def delete_video(video_id: str):
    """删除视频"""
    try:
        video = storage.get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")

        storage.delete_video(video_id)

        return {
            "success": True,
            "message": "视频已删除"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "success": True,
        "message": "服务正常运行",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
