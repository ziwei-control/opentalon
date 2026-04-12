---
name: shell-cmd
description: 执行安全的 Shell 命令
version: 0.1.0
author: OpenTalon Team
triggers:
  - "执行命令"
  - "运行"
  - "cmd"
  - "shell"
  - "bash"
permissions:
  - execute_safe_commands
warnings:
  - "危险命令需要确认"
  - "禁止 rm -rf / 等破坏性命令"
---

# Skill: shell-cmd

执行安全的 Shell 命令

## 安全规则

### ✅ 允许的命令

- `ls`, `dir` - 列出文件
- `pwd` - 显示当前目录
- `cat`, `head`, `tail` - 查看文件内容
- `grep`, `find` - 搜索
- `wc` - 统计
- `date`, `time` - 时间
- `echo` - 输出
- `cd` - 切换目录 (仅显示，不实际执行)
- `df`, `du` - 磁盘使用
- `ps` - 进程状态
- `netstat`, `ss` - 网络状态

### ❌ 禁止的命令

- `rm -rf /` 或任何递归删除
- `sudo` - 提权命令
- `curl * | bash` - 管道执行
- `wget * | bash` - 管道执行
- `dd` - 磁盘写入
- `mkfs` - 格式化
- 任何包含 `>/dev/sd*` 的命令

## 使用示例

```
用户：执行命令 ls -la

智能体：
$ ls -la
total 48
drwxr-xr-x  6 admin admin 4096 Apr  9 14:00 .
...
```

```
用户：运行 pwd

智能体：
$ pwd
/home/admin/projects/opentalon
```
