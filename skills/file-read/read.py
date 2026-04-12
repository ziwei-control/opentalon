#!/usr/bin/env python3
"""
file-read 技能实现

读取和总结本地文本文件
"""

import os
import re
from pathlib import Path

# 由技能加载器注入
user_input = ""
context = {}
workspace_path = "workspace/"

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = [
    '.txt', '.md', '.json', '.yaml', '.yml',
    '.py', '.js', '.ts', '.rs', '.go',
    '.java', '.c', '.cpp', '.h', '.hpp',
    '.rb', '.php', '.sh', '.bash', '.zsh',
    '.toml', '.ini', '.cfg', '.conf',
    '.xml', '.html', '.htm', '.css', '.scss',
    '.sql', '.graphql',
]

# 不支持的文件扩展名
UNSUPPORTED_EXTENSIONS = [
    '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg',
    '.mp3', '.mp4', '.avi', '.mov',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.exe', '.dll', '.so', '.bin',
]


def extract_filepath(user_input: str) -> str:
    """从用户输入中提取文件路径"""
    # 尝试提取引号内的内容
    quote_match = re.search(r'["](.*?)["]', user_input)
    if quote_match:
        return quote_match.group(1)
    
    # 尝试提取文件路径模式
    patterns = [
        r'(?:读取 | 查看 | 打开|read|cat|show|显示)\s*(?:文件\s*)?([^\s]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            filepath = match.group(1)
            # 清理路径
            filepath = filepath.rstrip('.,;:!?')
            return filepath
    
    return ""


def is_supported(filepath: str) -> tuple:
    """
    检查文件是否支持读取
    
    Returns:
        (is_supported: bool, reason: str)
    """
    path = Path(filepath)
    ext = path.suffix.lower()
    
    if not ext:
        return False, "文件没有扩展名"
    
    if ext in UNSUPPORTED_EXTENSIONS:
        return False, f"不支持的文件类型：{ext}"
    
    if ext in SUPPORTED_EXTENSIONS:
        return True, "支持"
    
    # 尝试检查文件类型
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            # 检查是否包含二进制内容
            if b'\x00' in chunk:
                return False, "检测到二进制内容"
        return True, "可能是文本文件"
    except:
        return False, "无法读取文件"


def read_file(filepath: str, max_lines: int = 100) -> str:
    """
    读取文件内容
    
    Args:
        filepath: 文件路径
        max_lines: 最大显示行数
    
    Returns:
        文件内容或错误信息
    """
    # 检查文件是否存在
    if not os.path.exists(filepath):
        # 尝试在工作空间查找
        workspace_filepath = Path(workspace_path) / filepath
        if workspace_filepath.exists():
            filepath = str(workspace_filepath)
        else:
            return f"❌ 文件不存在：{filepath}\n\n💡 提示：检查路径是否正确"
    
    # 检查是否支持
    supported, reason = is_supported(filepath)
    if not supported:
        return f"❌ {reason}\n\n💡 此文件类型需要专用工具读取"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        
        output = []
        output.append(f"📄 {filepath}")
        output.append("")
        
        # 如果文件很大，只显示前 max_lines 行
        if total_lines > max_lines:
            content = ''.join(lines[:max_lines])
            output.append(content)
            output.append("")
            output.append(f"(共 {total_lines} 行，显示前 {max_lines} 行)")
        else:
            content = ''.join(lines)
            output.append(content)
        
        return '\n'.join(output)
        
    except UnicodeDecodeError:
        return f"❌ 无法解码文件 (非 UTF-8 编码)\n\n💡 尝试指定编码或使用其他工具"
    except Exception as e:
        return f"❌ 读取失败：{str(e)}"


def summarize_file(filepath: str, max_chars: int = 2000) -> str:
    """
    总结文件内容
    
    Args:
        filepath: 文件路径
        max_chars: 最大字符数
    
    Returns:
        文件总结
    """
    if not os.path.exists(filepath):
        workspace_filepath = Path(workspace_path) / filepath
        if workspace_filepath.exists():
            filepath = str(workspace_filepath)
        else:
            return f"❌ 文件不存在：{filepath}"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 截断
        if len(content) > max_chars:
            content = content[:max_chars] + "\n...(省略)"
        
        # 生成总结
        output = []
        output.append(f"📄 {filepath}")
        output.append("")
        output.append(f"**文件大小**: {len(content)} 字符")
        output.append("")
        output.append("**内容摘要**:")
        output.append("")
        output.append(content)
        
        return '\n'.join(output)
        
    except Exception as e:
        return f"❌ 读取失败：{str(e)}"


def main():
    """主函数"""
    # 提取文件路径
    filepath = extract_filepath(user_input)
    
    if not filepath:
        return "❌ 未指定文件路径\n\n💡 用法：读取文件 <路径>"
    
    # 检查是否是总结请求
    if '总结' in user_input or 'summarize' in user_input.lower():
        return summarize_file(filepath)
    else:
        return read_file(filepath)


def run():
    """别名"""
    return main()


# 测试
if __name__ == "__main__":
    print("📄 file-read 技能测试")
    print("")
    
    test_cases = [
        "读取文件 README.md",
        "查看文件 workspace/SOUL.md",
        'read "opentalon.py"',
        "总结文件 README.md",
    ]
    
    for test_input in test_cases:
        filepath = extract_filepath(test_input)
        print(f"输入：{test_input}")
        print(f"提取路径：{filepath}")
        
        if filepath:
            supported, reason = is_supported(filepath)
            print(f"支持检查：{'✅' if supported else '❌'} {reason}")
        print("")
