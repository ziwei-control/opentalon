#!/usr/bin/env python3
"""
file-search 技能实现

在工作区内搜索文件内容
"""

import os
import re
from pathlib import Path
from typing import List, Dict

# 由技能加载器注入
user_input = ""
context = {}
workspace_path = "workspace/"


def search_files(query: str, path: str = "workspace/", 
                 include: List[str] = None, exclude: List[str] = None) -> Dict:
    """
    搜索文件内容
    
    Args:
        query: 搜索关键字
        path: 搜索路径
        include: 包含的文件模式
        exclude: 排除的文件/目录
    
    Returns:
        搜索结果字典
    """
    if include is None:
        include = ["*.md", "*.txt", "*.yaml", "*.yml", "*.json", "*.py"]
    if exclude is None:
        exclude = [".git", "__pycache__", "node_modules", ".pyc"]
    
    matches = []
    total_files = 0
    
    search_path = Path(path)
    
    for file_pattern in include:
        for file_path in search_path.rglob(file_pattern):
            # 检查是否在排除目录中
            if any(excl in str(file_path) for excl in exclude):
                continue
            
            total_files += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    if re.search(query, line, re.IGNORECASE):
                        # 获取上下文 (前后各 2 行)
                        context_start = max(0, line_num - 3)
                        context_end = min(len(lines), line_num + 2)
                        context_lines = lines[context_start:context_end]
                        
                        matches.append({
                            'file': str(file_path),
                            'line': line_num,
                            'content': line.strip(),
                            'context': ''.join(context_lines).strip()
                        })
            except Exception as e:
                continue
    
    return {
        'matches': matches,
        'summary': {
            'total_files': total_files,
            'total_matches': len(matches),
        }
    }


def format_result(result: Dict, query: str) -> str:
    """格式化搜索结果"""
    output = []
    
    output.append(f"🔍 搜索 \"{query}\"")
    output.append("")
    
    if not result['matches']:
        output.append("❌ 未找到匹配内容。")
        return '\n'.join(output)
    
    output.append(f"✅ 找到 {len(result['matches'])} 处匹配:\n")
    
    # 分组显示（按文件）
    files_dict = {}
    for match in result['matches']:
        file_path = match['file']
        if file_path not in files_dict:
            files_dict[file_path] = []
        files_dict[file_path].append(match)
    
    for file_path, file_matches in files_dict.items():
        output.append(f"**{file_path}** ({len(file_matches)} 处)")
        output.append("")
        
        for match in file_matches[:5]:  # 每个文件最多显示 5 处
            output.append(f"  第 {match['line']} 行：{match['content'][:80]}")
            if len(match['content']) > 80:
                output.append("")
        
        if len(file_matches) > 5:
            output.append(f"  ... 还有 {len(file_matches) - 5} 处")
        
        output.append("")
    
    output.append(f"---")
    output.append(f"共搜索 {result['summary']['total_files']} 个文件")
    
    return '\n'.join(output)


def extract_query(user_input: str) -> str:
    """从用户输入中提取搜索关键字"""
    # 尝试提取引号内的内容
    quote_match = re.search(r'[""](.*?)[""]', user_input)
    if quote_match:
        return quote_match.group(1)
    
    # 尝试提取"搜索"、"查找"、"grep"等关键词后的内容
    patterns = [
        r'(?:搜索 | 查找|grep|find)\s*[:：]?\s*(.+)',
        r'在.*?里 (?:找 | 搜索)\s*(.+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # 默认返回整个输入
    return user_input


def extract_path(user_input: str) -> str:
    """从用户输入中提取搜索路径"""
    # 查找路径模式
    path_match = re.search(r'(?:在 | 路径 | path)[:：\s]*(\S+)', user_input)
    if path_match:
        return path_match.group(1)
    
    # 默认路径
    return workspace_path


def main():
    """主函数"""
    # 提取查询和路径
    query = extract_query(user_input)
    path = extract_path(user_input)
    
    # 执行搜索
    result = search_files(query, path)
    
    # 格式化结果
    return format_result(result, query)


def run():
    """别名"""
    return main()


# 测试
if __name__ == "__main__":
    print("🔍 file-search 技能测试")
    print("")
    
    # 测试用例
    test_cases = [
        "搜索文件：决策",
        '查找"权限"',
        "grep 智能体",
        "在 workspace 里找 MEMORY"
    ]
    
    for test_input in test_cases:
        print(f"输入：{test_input}")
        print(f"提取查询：{extract_query(test_input)}")
        print(f"提取路径：{extract_path(test_input)}")
        print("")
