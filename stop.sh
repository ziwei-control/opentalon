#!/bin/bash
# OpenTalon 停止脚本

echo "🛑 停止 OpenTalon Web 服务..."

# 查找进程
PIDS=$(pgrep -f "web_server.py")

if [ -z "$PIDS" ]; then
    echo "✅ 服务未运行"
    exit 0
fi

echo "📋 找到进程:"
echo "$PIDS"

# 停止进程
pkill -f "web_server.py"

sleep 1

# 检查是否停止
if pgrep -f "web_server.py" > /dev/null; then
    echo "⚠️  强制停止..."
    pkill -9 -f "web_server.py"
fi

echo "✅ 服务已停止"
