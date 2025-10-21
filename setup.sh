#!/bin/bash
# YouTube 视频摘要工具 - 快速安装脚本

echo "🚀 开始安装 YouTube 视频摘要工具..."
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
python3 --version

# 创建虚拟环境
echo ""
echo "创建 Python 虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "安装依赖包（这可能需要几分钟）..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建配置文件
if [ ! -f .env ]; then
    echo ""
    echo "创建 .env 配置文件..."
    cp .env.example .env
    echo "✓ 已创建 .env 文件"
    echo ""
    echo "⚠️  请编辑 .env 文件，填入你的 API 密钥："
    echo "   - Anthropic (推荐): https://console.anthropic.com/"
    echo "   - OpenAI (可选): https://platform.openai.com/api-keys"
else
    echo ""
    echo "✓ .env 文件已存在"
fi

# 设置可执行权限
chmod +x main.py

echo ""
echo "✅ 安装完成！"
echo ""
echo "📖 快速开始："
echo "   1. 编辑 .env 文件，添加 API 密钥"
echo "   2. 激活虚拟环境: source venv/bin/activate"
echo "   3. 运行: python main.py --help"
echo ""
echo "💡 示例用法："
echo "   python main.py process 'https://www.youtube.com/watch?v=xxxxx'"
echo ""
