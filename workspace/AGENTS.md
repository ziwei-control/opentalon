---
# OpenTalon AGENTS.md - 多智能体协作规则
# 定义多智能体系统的路由、协作和记忆管理规范
---

## 🤖 智能体架构

### 单智能体模式 (默认)

```
用户 → Talon (主智能体) → 执行任务
```

适用于大多数场景，简单直接。

### 多智能体模式

```
用户 → Gateway (路由) → 专业智能体 → 结果汇总 → 用户
                      → 专业智能体 ↗
```

适用于复杂任务，需要多个专业智能体协作。

---

## 📋 智能体路由规则

### 按任务类型路由

| 任务类型 | 负责智能体 | 触发条件 |
|---------|-----------|---------|
| 日常对话 | Talon (通用) | 闲聊、问答、简单任务 |
| 代码开发 | DevBot | "写代码"、"debug"、"重构" |
| 数据分析 | DataBot | "分析"、"统计"、"可视化" |
| 文档写作 | DocBot | "写文档"、"翻译"、"润色" |
| 系统管理 | OpsBot | "部署"、"监控"、"运维" |
| 安全审计 | SecBot | "安全检查"、"审计"、"漏洞" |

### 按消息来源路由

| 消息来源 | 默认智能体 | 说明 |
|---------|-----------|------|
| Telegram | Talon | 即时消息，快速响应 |
| Discord | Talon | 社区互动，轻松风格 |
| 命令行 | OpsBot | 技术任务，精确执行 |
| 邮件 | DocBot | 正式沟通，详细回复 |

### 按优先级路由

| 优先级 | 处理方式 | 响应时间 |
|-------|---------|---------|
| 🔴 紧急 | 立即处理，打断当前任务 | < 1 分钟 |
| 🟡 普通 | 排队处理，按顺序执行 | < 10 分钟 |
| 🟢 低优 | 空闲时处理 | < 1 小时 |
| ⚪ 后台 | 定时任务，批量处理 | 按 cron |

---

## 🔄 协作流程

### 1. 任务分解

复杂任务由主智能体分解为子任务：

```
用户：帮我分析这个项目并写一份报告

Talon (主智能体):
  1. DevBot → 分析代码结构
  2. DataBot → 统计代码指标
  3. DocBot → 撰写报告
  4. Talon → 汇总并交付
```

### 2. 上下文共享

智能体之间共享必要上下文：

```yaml
shared_context:
  project_name: "OpenTalon"
  user_preference: "简洁直接"
  deadline: "2026-04-10"
  constraints:
    - "使用中文"
    - "代码示例要可运行"
```

### 3. 结果汇总

主智能体负责汇总各智能体结果：

```python
# 伪代码示例
def collaborate(task):
    subtasks = decompose(task)
    results = []
    
    for subtask in subtasks:
        agent = route(subtask)
        result = agent.execute(subtask, shared_context)
        results.append(result)
    
    return synthesize(results)
```

---

## 🧠 记忆管理规范

### 记忆层级

```
┌─────────────────────────────────────┐
│         USER.md                     │  ← 用户模型 (长期稳定)
│         - 基本信息                   │
│         - 偏好习惯                   │
├─────────────────────────────────────┤
│         MEMORY.md                   │  ← 长期记忆 (精选)
│         - 重要决策                   │
│         - 经验教训                   │
│         - 项目关键信息               │
├─────────────────────────────────────┤
│         memory/YYYY-MM-DD.md        │  ← 每日笔记 (原始记录)
│         - 对话记录                   │
│         - 临时信息                   │
│         - 待处理事项                 │
└─────────────────────────────────────┘
```

### 写入规则

| 信息类型 | 写入位置 | 保留时间 |
|---------|---------|---------|
| 用户偏好变更 | USER.md | 永久 |
| 重要决策 | MEMORY.md | 长期 |
| 项目进展 | MEMORY.md | 项目周期 |
| 日常对话 | memory/*.md | 30 天 |
| 临时信息 | memory/*.md | 7 天 |

### 检索规则

1. **会话开始** - 读取 USER.md + MEMORY.md
2. **任务执行** - 检索相关 memory/*.md
3. **定期回顾** - 提炼 memory/*.md → MEMORY.md

### 清理规则

```bash
# 伪代码：记忆维护任务
def memory_maintenance():
    # 7 天前的临时笔记标记为可清理
    old_notes = find_older_than("memory/", 7)
    
    # 提取有价值内容到 MEMORY.md
    for note in old_notes:
        valuable = extract_valuable(note)
        if valuable:
            append_to("MEMORY.md", valuable)
    
    # 清理过期笔记
    delete_older_than("memory/", 30)
```

---

## 🔐 安全与权限

### 权限级别

| 级别 | 权限范围 | 需要确认 |
|-----|---------|---------|
| L1 - 只读 | 读取文件、查询信息 | 否 |
| L2 - 写入 | 创建/修改文件 | 否 (工作区内) |
| L3 - 执行 | 运行命令、脚本 | 是 (破坏性命令) |
| L4 - 外部 | 发送邮件、推送代码 | 是 (必须) |
| L5 - 系统 | 安装软件、修改配置 | 是 (必须) |

### 智能体权限分配

| 智能体 | 默认权限 | 说明 |
|-------|---------|------|
| Talon | L2 | 通用助手 |
| DevBot | L3 | 代码执行 |
| OpsBot | L4 | 系统运维 |
| SecBot | L3 | 安全审计 |

### 安全沙箱

```yaml
sandbox:
  enabled: true
  allowed_paths:
    - /home/admin/projects/opentalon/workspace
    - /home/admin/projects/opentalon/skills
  blocked_commands:
    - "rm -rf /"
    - "sudo *"
    - "curl * | bash"
  network_access: restricted
```

---

## 📊 智能体状态管理

### 状态定义

| 状态 | 说明 | 转换条件 |
|-----|------|---------|
| IDLE | 空闲 | 无任务 |
| BUSY | 忙碌 | 执行任务中 |
| WAITING | 等待 | 等待用户确认 |
| ERROR | 错误 | 任务失败 |
| SLEEP | 休眠 | 定时任务间隔 |

### 状态持久化

```yaml
# gateway/state.yaml
agent_states:
  Talon:
    status: IDLE
    last_active: 2026-04-09T14:30:00
    current_task: null
  DevBot:
    status: BUSY
    last_active: 2026-04-09T14:25:00
    current_task: "analyze_code.py"
```

---

## 🎯 冲突解决

### 智能体意见分歧

当多个智能体给出不同建议时：

1. **列出所有方案** - 透明展示差异
2. **说明各自理由** - 解释每个方案的优劣
3. **给出推荐** - 主智能体综合判断
4. **让用户决定** - 最终选择权在用户

### 示例

```
任务：选择数据库

DevBot 推荐: PostgreSQL
  - 理由：ACID 合规，适合复杂查询

OpsBot 推荐: MongoDB
  - 理由：部署简单，扩展容易

Talon 综合建议:
  根据你的项目特点 (需要复杂查询 + 数据一致性重要)
  推荐 PostgreSQL

  你希望选哪个？
```

---

## 📝 配置示例

### 路由配置 (gateway/routes.yaml)

```yaml
routes:
  - pattern: ".*代码.*|.*debug.*|.*bug.*"
    agent: DevBot
    priority: high
    
  - pattern: ".*分析.*|.*数据.*|.*统计.*"
    agent: DataBot
    priority: normal
    
  - pattern: ".*部署.*|.*运维.*|.*服务器.*"
    agent: OpsBot
    priority: high
    
  - default: Talon
```

### 智能体配置 (gateway/agents.yaml)

```yaml
agents:
  Talon:
    type: general
    personality: workspace/SOUL.md
    permissions: [L2]
    
  DevBot:
    type: specialist
    specialty: development
    permissions: [L3]
    
  OpsBot:
    type: specialist
    specialty: operations
    permissions: [L4]
```

---

## 🔄 更新历史

| 日期 | 更新内容 | 版本 |
|------|---------|------|
| 2026-04-09 | 初始版本 | v0.1.0 |

---

_这份文件定义多智能体如何协作。随着系统发展持续完善。_
