---
name: file-read
description: 读取和总结本地文本文件
version: 0.1.0
author: OpenTalon Team
triggers:
  - "读取文件"
  - "查看文件"
  - "打开文件"
  - "read"
  - "cat"
  - "show"
  - "显示"
permissions:
  - read_files
supported_formats:
  - ".txt"
  - ".md"
  - ".json"
  - ".yaml"
  - ".yml"
  - ".py"
  - ".js"
  - ".ts"
  - ".rs"
  - ".go"
  - ".java"
  - ".c"
  - ".cpp"
  - ".h"
  - ".hpp"
---

# Skill: file-read

读取和总结本地文本文件

## 支持的文件类型

### 文本文件 ✅

- `.txt` - 纯文本
- `.md` - Markdown
- `.json` - JSON
- `.yaml/.yml` - YAML
- 代码文件 - `.py`, `.js`, `.ts`, `.rs`, `.go`, `.java`, `.c`, `.cpp`, `.h`

### 不支持的文件 ❌

- `.pdf` - PDF 文档 (需要专用工具)
- `.docx` - Word 文档 (需要专用工具)
- `.xlsx` - Excel 表格 (需要专用工具)
- 图片 - `.png`, `.jpg`, `.gif`
- 音频/视频

## 使用示例

```
用户：读取文件 README.md

智能体：
📄 README.md (前 50 行)

# OpenTalon 项目

这是一个 Markdown 驱动的智能体项目...

(共 180 行，显示前 50 行)
```

```
用户：查看文件 workspace/SOUL.md 的内容

智能体：
📄 workspace/SOUL.md

[文件内容...]
```
