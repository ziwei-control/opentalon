#!/usr/bin/env python3
"""
shell-cmd 技能实现

执行安全的 Shell 命令
"""

import os
import re
import subprocess
from pathlib import Path

# 由技能加载器注入
user_input = ""
context = {}
workspace_path = "workspace/"

# 安全命令白名单
SAFE_COMMANDS = [
    'ls', 'dir', 'pwd', 'cat', 'head', 'tail', 'grep', 'find',
    'wc', 'date', 'time', 'echo', 'df', 'du', 'ps', 'netstat', 'ss',
    'whoami', 'hostname', 'uname', 'which', 'whereis', 'file',
    'stat', 'touch', 'mkdir', 'cp', 'mv', 'chmod', 'chown',
    'sort', 'uniq', 'cut', 'awk', 'sed', 'tr', 'tee',
    'zip', 'unzip', 'tar', 'gzip',
]

# 危险命令黑名单
DANGEROUS_PATTERNS = [
    r'rm\s+(-[rf]+\s+)?/',  # rm -rf /
    r'rm\s+-rf\s+\*',       # rm -rf *
    r'sudo',                 # sudo
    r'curl.*\|\s*(ba)?sh',   # curl | bash
    r'wget.*\|\s*(ba)?sh',   # wget | bash
    r'dd\s+',                # dd
    r'mkfs',                 # mkfs
    r'>\s*/dev/sd',          # 写入磁盘
    r'mkfs',                 # 格式化
    r'chmod\s+777',          # 危险权限
]


def is_safe_command(command: str) -> tuple:
    """
    检查命令是否安全
    
    Returns:
        (is_safe: bool, reason: str)
    """
    # 提取命令名
    parts = command.strip().split()
    if not parts:
        return False, "空命令"
    
    cmd_name = parts[0]
    
    # 检查是否在白名单
    if cmd_name not in SAFE_COMMANDS:
        return False, f"命令 '{cmd_name}' 不在白名单中"
    
    # 检查危险模式
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"命令包含危险模式：{pattern}"
    
    return True, "安全"


def extract_command(user_input: str) -> str:
    """从用户输入中提取命令"""
    # 尝试提取引号内的内容
    quote_match = re.search(r'["](.*?)["]', user_input)
    if quote_match:
        return quote_match.group(1)
    
    # 尝试提取命令关键词后的内容
    patterns = [
        r'(?:执行命令 | 运行|cmd|shell|bash)\s*[:：]?\s*(.+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # 默认返回整个输入
    return user_input


def execute_command(command: str) -> str:
    """
    执行命令并返回结果
    
    Args:
        command: 要执行的命令
    
    Returns:
        命令输出或错误信息
    """
    # 安全检查
    is_safe, reason = is_safe_command(command)
    
    if not is_safe:
        return f"❌ 命令被阻止：{reason}\n\n💡 为了安全，某些命令被禁止执行。\n如需执行危险命令，请在终端中手动运行。"
    
    try:
        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=workspace_path
        )
        
        output = []
        
        # 显示执行的命令
        output.append(f"$ {command}")
        output.append("")
        
        # 标准输出
        if result.stdout:
            output.append(result.stdout)
        
        # 标准错误
        if result.stderr:
            output.append(f"[错误] {result.stderr}")
        
        # 返回码
        if result.returncode != 0:
            output.append(f"\n[返回码] {result.returncode}")
        
        return '\n'.join(output)
        
    except subprocess.TimeoutExpired:
        return f"❌ 命令执行超时 (>30 秒)"
    except Exception as e:
        return f"❌ 执行失败：{str(e)}"


def main():
    """主函数"""
    # 提取命令
    command = extract_command(user_input)
    
    # 执行并返回结果
    return execute_command(command)


def run():
    """别名"""
    return main()


# 测试
if __name__ == "__main__":
    print("🔧 shell-cmd 技能测试")
    print("")
    
    test_cases = [
        "执行命令 ls -la",
        "运行 pwd",
        "shell: cat README.md",
        "rm -rf /",  # 危险命令
        "sudo apt update",  # 危险命令
    ]
    
    for test_input in test_cases:
        command = extract_command(test_input)
        print(f"输入：{test_input}")
        print(f"提取命令：{command}")
        
        is_safe, reason = is_safe_command(command)
        print(f"安全检查：{'✅' if is_safe else '❌'} {reason}")
        print("")
