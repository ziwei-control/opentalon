# ✅ OpenTalon 完整使用指南

**更新时间**: 2026-04-12  
**版本**: v0.2.0

---

## 🎉 回答你的问题

### ❓ 问题 1: LLM 可以配云模型吗？Kimi2.5 和 Qwen3.5 可以用吗？

**✅ 完全可以!**

OpenTalon 支持所有 OpenAI 兼容 API 的云模型，包括：

| 云模型 | 状态 | 配置难度 |
|--------|------|---------|
| **Kimi2.5** (月之暗面) | ✅ 支持 | ⭐ 简单 |
| **Qwen3.5** (通义千问) | ✅ 支持 | ⭐ 简单 |
| DeepSeek | ✅ 支持 | ⭐ 简单 |
| OpenAI GPT | ✅ 支持 | ⭐ 简单 |
| Zhipu GLM | ✅ 支持 | ⭐ 简单 |
| Baichuan | ✅ 支持 | ⭐ 简单 |

---

### ❓ 问题 2: OpenTalon 可以网页访问吗？

**✅ 可以!**

OpenTalon 提供 Web 界面，可以通过浏览器访问：

```bash
# 启动 Web 服务
./start_web.sh

# 访问地址
http://localhost:8080
```

**Web 界面功能**:
- 💬 实时对话聊天
- 📊 配置状态显示
- 🎨 美观的响应式设计
- 📱 支持手机访问
- ⌨️ 回车发送消息

---

## 🚀 完整使用流程

### 步骤 1: 配置 Kimi2.5 或 Qwen3.5

#### 方式 A: 交互式配置 (推荐)

```bash
cd /home/admin/projects/opentalon
python3 configure_llm.py
```

**选择提供商**:
```
2. Kimi (月之暗面) - Kimi2.5
3. Qwen (通义千问) - Qwen3.5
```

**输入 API Key**:
- Kimi: https://platform.moonshot.cn/
- Qwen: https://dashscope.console.aliyun.com/

#### 方式 B: 手动配置

**Kimi2.5 配置**:
```bash
cat > ~/.opentalon/llm_config.json << 'EOF'
{
  "provider": "openai",
  "api_key": "sk-your-kimi-key",
  "base_url": "https://api.moonshot.cn/v1",
  "model": "kimi-latest",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 60
}
EOF
```

**Qwen3.5 配置**:
```bash
cat > ~/.opentalon/llm_config.json << 'EOF'
{
  "provider": "openai",
  "api_key": "sk-your-qwen-key",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-max",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 60
}
EOF
```

---

### 步骤 2: 验证配置

```bash
python3 opentalon.py configure
```

**成功输出**:
```
⚙️  LLM 配置信息:

  ✅ 配置文件：/home/admin/.opentalon/llm_config.json
  ✅ Provider: openai
  ✅ Model: kimi-latest (或 qwen-max)
  ✅ Base URL: https://api.moonshot.cn/v1 (或阿里云)
  ✅ API Key: sk-your...xxx
```

---

### 步骤 3: 启动使用

#### 方式 A: Web 网页访问 ⭐ 推荐

```bash
# 1. 安装 Flask (首次需要)
pip3 install flask flask-cors

# 2. 启动 Web 服务
./start_web.sh

# 3. 打开浏览器访问
# http://localhost:8080
```

**Web 界面特点**:
- 🎨 美观的聊天界面
- 💬 实时对话
- 📊 显示配置状态
- 📱 手机也能访问
- ⌨️ 回车发送

**自定义端口**:
```bash
python3 web_server.py --port 9000
# 访问 http://localhost:9000
```

**局域网访问**:
```bash
python3 web_server.py --host 0.0.0.0 --port 8080
# 其他设备访问 http://你的IP:8080
```

#### 方式 B: CLI 命令行

```bash
python3 opentalon.py cli
```

**CLI 内部命令**:
```
🤖 Talon > help          # 帮助
🤖 Talon > skills        # 技能列表
🤖 Talon > memory        # 查看记忆
🤖 Talon > config        # 查看配置
🤖 Talon > clear         # 清屏
🤖 Talon > exit          # 退出
```

---

## 📊 Kimi2.5 vs Qwen3.5 对比

| 特性 | Kimi2.5 | Qwen3.5 |
|------|---------|---------|
| **提供商** | 月之暗面 | 阿里巴巴 |
| **最强项** | 128K 上下文 | 代码能力 |
| **适合场景** | 长文档分析 | 编程开发 |
| **中文能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **代码能力** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **价格** | ¥12/M | ¥40/M |
| **API 端点** | moonshot.cn | aliyuncs.com |

**推荐选择**:
- 📄 **长文档/论文分析**: Kimi2.5 (128K 上下文)
- 💻 **代码开发/调试**: Qwen3.5 (代码优化好)
- 💰 **性价比**: Kimi2.5 (价格便宜)
- 🏢 **企业应用**: Qwen3.5 (阿里生态)

---

## 🎯 实际使用示例

### Web 界面使用

1. **启动服务**
   ```bash
   ./start_web.sh
   ```

2. **打开浏览器**
   ```
   http://localhost:8080
   ```

3. **开始对话**
   ```
   你好，介绍一下你自己
   ```

4. **继续提问**
   ```
   帮我分析一下这个项目的架构
   ```

5. **查看文件**
   ```
   搜索 MEMORY.md 里关于"决策"的内容
   ```

### CLI 使用

```bash
$ python3 opentalon.py cli

🤖 Talon > 你好，我是新用户

🤖 Talon > 欢迎！我是 Talon，一个 Markdown 驱动的
           本地化智能体。很高兴为你服务！
           
           有什么可以帮你的吗？

🤖 Talon > 帮我总结一下今天的记忆

🤖 Talon > 📊 今日记忆摘要：
           - 完成事项：3 项
           - 关键决策：1 项
           ...

🤖 Talon > exit
👋 再见！
```

---

## 🔧 常用命令速查

```bash
# ========== 配置 ==========
python3 configure_llm.py          # 配置云模型
python3 opentalon.py configure    # 查看 LLM 配置
python3 opentalon.py config       # 查看项目配置

# ========== 使用 ==========
./start_web.sh                    # 启动 Web 服务 ⭐
python3 opentalon.py cli          # 启动 CLI

# ========== 技能 ==========
python3 opentalon.py skills list  # 列出技能
python3 opentalon.py memory       # 查看记忆

# ========== 帮助 ==========
python3 opentalon.py              # 查看所有命令
cat QUICKSTART.md                 # 快速开始指南
cat CLOUD_MODEL_SETUP.md          # 云模型配置详解
```

---

## 📁 项目文件结构

```
opentalon/
├── QUICKSTART.md              # 本文件 - 快速开始 ⭐
├── README.md                  # 项目说明
├── CLOUD_MODEL_SETUP.md       # 云模型配置指南
├── configure_llm.py           # 配置工具
├── web_server.py              # Web 服务器 ⭐
├── start_web.sh               # Web 启动脚本 ⭐
├── opentalon.py               # 主程序
│
├── workspace/                 # 工作空间
│   ├── SOUL.md               # 智能体人格
│   ├── USER.md               # 用户偏好
│   ├── AGENTS.md             # 协作规则
│   ├── MEMORY.md             # 长期记忆
│   └── memory/               # 每日笔记
│
├── skills/                    # 技能目录
│   └── file-search/          # 文件搜索技能
│
├── channels/                  # 通道配置
│   └── cli.yaml              # CLI 通道
│
└── gateway/                   # 网关配置
    └── routes.yaml           # 路由规则
```

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

**原因**: API Key 无效

**解决**:
```bash
# 重新配置
python3 configure_llm.py

# 或手动修改
vim ~/.opentalon/llm_config.json
```

### 问题 4: Web 无法访问

**检查端口**:
```bash
netstat -tlnp | grep 8080
```

**检查防火墙**:
```bash
# 如果是云服务器，需要开放端口
```

### 问题 5: Kimi/Qwen API Key 获取

**Kimi**:
1. 访问 https://platform.moonshot.cn/
2. 注册/登录
3. 控制台 → API Key 管理
4. 创建新 Key

**Qwen**:
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录阿里云
3. 控制台 → API Key 管理
4. 创建新 Key

---

## 📚 详细文档

| 文档 | 说明 |
|------|------|
| `QUICKSTART.md` | 本文件 - 快速开始指南 |
| `README.md` | 项目总览和架构 |
| `CLOUD_MODEL_SETUP.md` | 云模型详细配置 |
| `CLOUD_MODEL_COMPLETE.md` | 配置完成总结 |
| `OPENTALON_TIMELINE.md` | 项目时间线 |
| `workspace/SOUL.md` | 智能体人格定义 |
| `workspace/USER.md` | 用户偏好模板 |

---

## 💡 使用技巧

### 1. 切换云模型

有多个 API Key 时可以快速切换：

```bash
# 备份当前配置
cp ~/.opentalon/llm_config.json ~/.opentalon/llm_config.backup.json

# 使用 Kimi
cp ~/.opentalon/llm_config.kimi.example.json ~/.opentalon/llm_config.json
# 编辑填入 API Key

# 使用 Qwen
cp ~/.opentalon/llm_config.qwen.example.json ~/.opentalon/llm_config.json
# 编辑填入 API Key
```

### 2. 自定义 Web 端口

```bash
python3 web_server.py --port 9000
```

### 3. 局域网访问

```bash
python3 web_server.py --host 0.0.0.0 --port 8080
```

然后其他设备访问 `http://你的IP:8080`

### 4. 查看 API 使用量

在云模型控制台查看：
- Kimi: https://platform.moonshot.cn/
- Qwen: https://dashscope.console.aliyun.com/

---

## 🎯 总结

### ✅ 你的两个问题

1. **LLM 可以配云模型吗？Kimi2.5 和 Qwen3.5 可以用吗？**
   - ✅ **可以!** 完全支持，配置简单

2. **OpenTalon 可以网页访问吗？**
   - ✅ **可以!** 启动 Web 服务即可

### 🚀 快速开始

```bash
# 1. 配置云模型
python3 configure_llm.py

# 2. 安装 Web 依赖
pip3 install flask flask-cors

# 3. 启动 Web 服务
./start_web.sh

# 4. 访问
# http://localhost:8080
```

**就这么简单!** 🎉

---

**项目状态**: ✅ 云模型配置完成 + Web 界面完成  
**最后更新**: 2026-04-12  
**版本**: v0.2.0
