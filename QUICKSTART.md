# 🚀 OpenTalon 快速使用指南

**更新时间**: 2026-04-12  
**版本**: v0.2.0

---

## ✅ 功能概览

| 功能 | 状态 | 说明 |
|------|------|------|
| **云模型支持** | ✅ 完成 | Kimi2.5, Qwen3.5, DeepSeek 等 |
| **CLI 交互** | ✅ 完成 | 命令行对话 |
| **Web 界面** | ✅ 完成 | 网页访问 |
| **文件搜索** | 🚧 开发中 | 技能框架 |
| **记忆系统** | ✅ 完成 | Markdown 记忆 |

---

## ⚡ 5 分钟快速开始

### 步骤 1: 配置云模型 (必需)

**支持 Kimi2.5 和 Qwen3.5!**

```bash
cd /home/admin/projects/opentalon
python3 configure_llm.py
```

**选择提供商**:
```
2. Kimi (月之暗面) - Kimi2.5
3. Qwen (通义千问) - Qwen3.5
```

#### Kimi2.5 配置

```json
{
  "provider": "openai",
  "api_key": "sk-your-kimi-key",
  "base_url": "https://api.moonshot.cn/v1",
  "model": "kimi-latest"
}
```

**获取 API Key**: https://platform.moonshot.cn/

#### Qwen3.5 配置

```json
{
  "provider": "openai",
  "api_key": "sk-your-qwen-key",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-max"
}
```

**获取 API Key**: https://dashscope.console.aliyun.com/

---

### 步骤 2: 验证配置

```bash
python3 opentalon.py configure
```

看到 `✅` 表示配置成功。

---

### 步骤 3: 选择使用方式

#### 方式 A: CLI 命令行

```bash
python3 opentalon.py cli
```

#### 方式 B: Web 网页访问 ⭐ 推荐

```bash
# 安装 Flask (首次需要)
pip3 install flask flask-cors

# 启动 Web 服务
./start_web.sh

# 或使用默认端口
python3 web_server.py
```

**访问**: http://localhost:8080

---

## 🌐 Web 界面使用

### 启动 Web 服务

```bash
cd /home/admin/projects/opentalon

# 方式 1: 使用启动脚本
./start_web.sh

# 方式 2: 自定义端口
python3 web_server.py --port 9000

# 方式 3: 指定监听地址
python3 web_server.py --host 0.0.0.0 --port 8080
```

### 访问地址

| 场景 | 地址 |
|------|------|
| **本地访问** | http://localhost:8080 |
| **局域网访问** | http://你的IP:8080 |
| **自定义端口** | http://localhost:你的端口 |

### Web 界面功能

- 💬 实时对话
- 📊 配置状态显示
- 🎨 美观界面
- 📱 响应式设计
- ⌨️ 回车发送

---

## 💬 CLI 使用

### 启动

```bash
python3 opentalon.py cli
```

### 内部命令

```
🤖 Talon > help          # 帮助
🤖 Talon > skills        # 技能列表
🤖 Talon > memory        # 查看记忆
🤖 Talon > config        # 查看配置
🤖 Talon > clear         # 清屏
🤖 Talon > exit          # 退出
```

---

## 📁 配置文件

### 云模型配置

**位置**: `~/.opentalon/llm_config.json`

**示例 (Kimi2.5)**:
```json
{
  "provider": "openai",
  "api_key": "sk-kimi-your-key",
  "base_url": "https://api.moonshot.cn/v1",
  "model": "kimi-latest",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 60
}
```

**示例 (Qwen3.5)**:
```json
{
  "provider": "openai",
  "api_key": "sk-qwen-your-key",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-max",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 60
}
```

### 智能体人格

```bash
vim workspace/SOUL.md
```

### 用户偏好

```bash
vim workspace/USER.md
```

---

## 🔧 常用命令

```bash
# 配置云模型
python3 configure_llm.py

# 查看 LLM 配置
python3 opentalon.py configure

# 查看项目配置
python3 opentalon.py config

# CLI 交互
python3 opentalon.py cli

# Web 服务
./start_web.sh
python3 web_server.py

# 列出技能
python3 opentalon.py skills list

# 查看记忆
python3 opentalon.py memory

# 快速启动 (CLI)
./setup_and_start.sh

# 快速启动 (Web)
./start_web.sh
```

---

## 💡 使用示例

### Web 界面示例

1. 启动 Web 服务
   ```bash
   ./start_web.sh
   ```

2. 打开浏览器访问 http://localhost:8080

3. 在聊天框输入问题:
   ```
   你好，介绍一下你自己
   ```

4. 看到 Talon 的回复

5. 继续对话...

### CLI 示例

```bash
$ python3 opentalon.py cli

🤖 Talon > 你好

🤖 Talon > 你好！我是 Talon，一个 Markdown 驱动的
           本地化智能体。有什么可以帮你的吗？

🤖 Talon > 帮我搜索 MEMORY.md 里关于"决策"的内容

🤖 Talon > 找到 3 处匹配：
           **MEMORY.md:15**
           > ### 重要决策
           ...

🤖 Talon > exit
👋 再见!
```

---

## 📊 云模型对比

| 提供商 | 模型 | 优势 | 价格 |
|--------|------|------|------|
| **Kimi** | kimi-latest (2.5) | 128K 上下文，长文档 | ¥12/M |
| **Qwen** | qwen-max (3.5) | 阿里出品，代码强 | ¥40/M |
| **DeepSeek** | deepseek-chat | 性价比高 | ¥1/M |

**推荐**:
- 📄 **长文档分析**: Kimi2.5 (128K 上下文)
- 💻 **代码开发**: Qwen3.5 (代码优化)
- 💰 **日常使用**: DeepSeek (便宜)

---

## ⚠️ 故障排除

### 问题 1: "Flask 未安装"

```bash
pip3 install flask flask-cors
```

### 问题 2: "LLM 未配置"

```bash
python3 configure_llm.py
```

### 问题 3: "401 Unauthorized"

检查 API Key 是否正确:
```bash
cat ~/.opentalon/llm_config.json
```

### 问题 4: Web 无法访问

检查防火墙:
```bash
# 查看端口
netstat -tlnp | grep 8080

# 如果是云服务器，开放端口
```

---

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| `README.md` | 项目总览 |
| `QUICKSTART.md` | 本文件 - 快速开始 |
| `CLOUD_MODEL_SETUP.md` | 云模型详细配置 |
| `CLOUD_MODEL_COMPLETE.md` | 配置完成总结 |
| `workspace/SOUL.md` | 智能体人格 |
| `workspace/USER.md` | 用户偏好 |

---

**需要帮助？**

运行 `python3 opentalon.py` 查看所有可用命令。

**项目状态**: 🚧 开发中  
**最后更新**: 2026-04-12
