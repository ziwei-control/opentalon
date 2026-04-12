#!/bin/bash
# OpenTalon 快速启动脚本 (修复版)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "🚀 OpenTalon 快速启动"
echo "======================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：需要 Python 3"
    exit 1
fi

# 检查 Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask 未安装，正在安装..."
    pip3 install flask flask-cors
fi

# 检查 LLM 配置
CONFIG_FILE=~/.opentalon/llm_config.json
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  未检测到 LLM 配置"
    echo "💡 提示：访问网页后可以在配置页设置 API Key"
fi

# 创建日志目录
mkdir -p logs

# 检查是否已在运行
if pgrep -f "web_server.py.*6767" > /dev/null; then
    echo "✅ Web 服务已在运行"
    PID=$(pgrep -f "web_server.py.*6767")
    echo "   进程 ID: $PID"
else
    echo "🚀 启动 Web 服务..."
    nohup python3 web_server.py --port 6767 > logs/web.log 2>&1 &
    sleep 2
    
    if pgrep -f "web_server.py.*6767" > /dev/null; then
        echo "✅ 启动成功!"
        PID=$(pgrep -f "web_server.py.*6767")
        echo "   进程 ID: $PID"
    else
        echo "❌ 启动失败，查看日志:"
        cat logs/web.log
        exit 1
    fi
fi

echo ""
echo "======================================"
echo "🌐 访问地址"
echo "======================================"
echo ""

# 获取本机 IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "✅ 本地访问：http://localhost:6767"
echo "✅ 局域网访问：http://$LOCAL_IP:6767"
echo "✅ 公网访问：http://你的公网IP:6767"
echo ""
echo "💡 提示:"
echo "   - 公网访问需要开放防火墙 6767 端口"
echo "   - 查看日志：tail -f logs/web.log"
echo "   - 停止服务：./stop.sh 或 pkill -f web_server.py"
echo ""

# 显示日志
echo "📋 最近日志:"
tail -5 logs/web.log
echo ""
