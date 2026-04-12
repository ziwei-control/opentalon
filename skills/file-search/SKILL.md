---
name: file-search
description: 在工作区内搜索文件内容，支持 grep 风格的关键字搜索
version: 0.1.0
author: OpenTalon Team
triggers:
  - "搜索"
  - "查找"
  - "grep"
  - "find"
  - "在.*里找"
  - "search"
permissions:
  - read_files
  - search_content
---

# Skill: file-search

在工作区搜索文件内容

## 触发条件

---

## 权限要求

- ✅ 读取文件
- ✅ 搜索内容
- ❌ 修改文件
- ❌ 执行命令

---

## 输入参数

```yaml
query: string        # 搜索关键字
path: string         # 搜索路径 (默认：workspace/)
include: string[]    # 包含的文件类型 (默认：["*.md"])
exclude: string[]    # 排除的文件/目录
```

---

## 输出格式

```yaml
matches:
  - file: string     # 文件路径
    line: number     # 行号
    content: string  # 匹配内容
    context: string  # 上下文 (前后各 2 行)
    
summary:
  total_files: number
  total_matches: number
  search_time: number  # 毫秒
```

---

## 使用示例

### 示例 1: 搜索关键字

```
用户：搜索一下 MEMORY.md 里关于"决策"的内容

智能体：
找到 3 处匹配：

**MEMORY.md:15**
> ### 重要决策
> 
> ### 架构设计

**MEMORY.md:23**
> | 决策 | 日期 | 原因 | 状态 |
> |------|------|------|------|

**MEMORY.md:42**
> 值得写入 MEMORY.md 的内容：
> - ✅ 重要决策和原因

共 3 处匹配，耗时 12ms
```

### 示例 2: 指定路径搜索

```
用户：在 skills 目录里找所有提到"权限"的文件

智能体：
在 skills/ 目录下搜索 "权限"...

找到 2 个文件：
- skills/file-search/SKILL.md (3 处)
- skills/template/SKILL.md (1 处)
```

---

## 实现脚本

```python
#!/usr/bin/env python3
"""
file-search skill implementation
搜索工作区内的文件内容
"""

import os
import re
from pathlib import Path
from typing import List, Dict

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
        include = ["*.md"]
    if exclude is None:
        exclude = [".git", "__pycache__", "node_modules"]
    
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
                        context = ''.join(lines[context_start:context_end])
                        
                        matches.append({
                            'file': str(file_path),
                            'line': line_num,
                            'content': line.strip(),
                            'context': context.strip()
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

def format_result(result: Dict) -> str:
    """格式化搜索结果"""
    output = []
    
    if not result['matches']:
        return "未找到匹配内容。"
    
    output.append(f"找到 {len(result['matches'])} 处匹配:\n")
    
    for match in result['matches']:
        output.append(f"**{match['file']}:{match['line']}**")
        output.append(f"> {match['content']}\n")
    
    output.append(f"共搜索 {result['summary']['total_files']} 个文件")
    
    return '\n'.join(output)

# 主函数
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python file_search.py <搜索关键字> [路径]")
        sys.exit(1)
    
    query = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) > 2 else "workspace/"
    
    result = search_files(query, path)
    print(format_result(result))
```

---

## 测试用例

```bash
# 测试 1: 基本搜索
python skills/file-search/search.py "决策"

# 测试 2: 指定路径
python skills/file-search/search.py "权限" skills/

# 测试 3: 正则搜索
python skills/file-search/search.py "TODO|FIXME"
```

---

## 更新历史

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-04-09 | 0.1.0 | 初始版本 |

---

## 许可证

MIT License
