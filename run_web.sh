#!/bin/bash
# Web 应用快速启动脚本

echo "🚀 启动 YouTube 视频摘要工具 Web 版..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  未找到虚拟环境，请先运行 ./setup.sh"
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 配置文件"
    echo "请复制 .env.example 为 .env 并填入 API 密钥"
    exit 1
fi

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 启动服务器
echo ""
echo "✅ 准备就绪！"
echo "📍 Web 界面: http://localhost:8000"
echo "📍 API 文档: http://localhost:8000/docs"
echo ""
echo "⚠️  按 Ctrl+C 停止服务器"
echo ""

python run_web.py
