#!/bin/bash
# OpenTalon Web 服务启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "🌐 OpenTalon Web 服务"
echo "======================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：需要 Python 3"
    exit 1
fi

# 检查 Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask 未安装"
    echo ""
    read -p "是否安装 Flask? (y/n): " choice
    
    if [ "$choice" = "y" ]; then
        echo "📦 安装 Flask..."
        pip3 install flask flask-cors
    else
        echo "❌ 需要 Flask 才能运行 Web 服务"
        exit 1
    fi
fi

# 检查 LLM 配置
CONFIG_FILE=~/.opentalon/llm_config.json
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  未检测到 LLM 配置"
    echo ""
    read -p "是否先配置 LLM? (y/n): " choice
    
    if [ "$choice" = "y" ]; then
        python3 configure_llm.py
    else
        echo "💡 提示：配置 LLM 后才能使用对话功能"
    fi
fi

echo ""
echo "======================================"
echo "🌐 OpenTalon Web 服务 (公网可访问)"
echo "======================================"
echo ""
echo "📍 监听地址：0.0.0.0:$PORT"
echo "🌍 访问地址："
echo "   - 本地：http://localhost:$PORT"
echo "   - 公网：http://你的公网IP:$PORT"
echo ""
echo "💡 提示:"
echo "   - 确保防火墙/安全组开放 $PORT 端口"
echo "   - 按 Ctrl+C 停止服务"
echo ""

python3 web_server.py --host $HOST --port $PORT
