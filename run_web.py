#!/usr/bin/env python3
"""Web 应用启动脚本"""

import uvicorn
import sys
import os

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 启动 YouTube 视频摘要工具 Web 应用...")
    print("📍 访问地址: http://localhost:8000")
    print("📍 API 文档: http://localhost:8000/docs")
    print("⚠️  按 Ctrl+C 停止服务器\n")

    uvicorn.run(
        "web.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式：代码改动自动重启
        log_level="info"
    )
