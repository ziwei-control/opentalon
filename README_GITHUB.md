# 🤖 OpenTalon

**Markdown 驱动的本地化自主智能体系统**

> "Markdown is the Soul" - 配置文件完全可读可编辑

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Cloud Models](https://img.shields.io/badge/cloud-Kimi%2FQwen%2FDeepSeek-green)](https://github.com/admin/opentalon)

---

## 🌟 特性

- **📝 Markdown 驱动**: 所有配置都是可读可编辑的 Markdown 文件
- **☁️ 云模型支持**: Kimi2.5, Qwen3.5, DeepSeek, OpenAI 等 6+ 云模型
- **🌐 Web 界面**: 美观的网页聊天界面，支持公网访问
- **💬 CLI 交互**: 命令行对话，轻量高效
- **🔧 技能系统**: 可扩展的技能框架
- **📚 记忆系统**: 长期记忆 + 每日笔记
- **🔒 隐私优先**: 本地部署，数据可控

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install flask flask-cors
```

### 2. 启动 Web 服务

```bash
./start.sh
```

### 3. 访问界面

- **本地**: http://localhost:6767
- **公网**: http://你的IP:6767

### 4. 配置 API Key

在网页配置页选择云模型并输入 API Key。

---

## ☁️ 支持的云模型

| 提供商 | 模型 | 官网 |
|--------|------|------|
| **Kimi** (月之暗面) | kimi-latest | [moonshot.cn](https://platform.moonshot.cn/) |
| **Qwen** (通义千问) | qwen-max | [aliyun.com](https://dashscope.console.aliyun.com/) |
| **DeepSeek** | deepseek-chat | [deepseek.com](https://platform.deepseek.com/) |
| **OpenAI** | gpt-4 | [openai.com](https://platform.openai.com/) |
| **Zhipu** (智谱) | glm-4 | [bigmodel.cn](https://open.bigmodel.cn/) |
| **Baichuan** | Baichuan4 | [baichuan-ai.com](https://platform.baichuan-ai.com/) |

---

## 📁 项目结构

```
opentalon/
├── opentalon.py           # 主程序
├── web_server.py          # Web 服务器
├── configure_llm.py       # 配置工具
├── start.sh               # 快速启动
├── stop.sh                # 停止服务
│
├── workspace/             # 工作空间
│   ├── SOUL.md           # 智能体人格
│   ├── USER.md           # 用户偏好
│   ├── AGENTS.md         # 协作规则
│   └── MEMORY.md         # 长期记忆
│
├── skills/                # 技能目录
│   └── file-read/        # 文件读取技能
│
├── channels/              # 通道配置
│   └── cli.yaml          # CLI 通道
│
└── gateway/               # 网关配置
    └── routes.yaml       # 路由规则
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 快速开始指南 |
| [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) | 完整使用指南 |
| [CLOUD_MODEL_SETUP.md](CLOUD_MODEL_SETUP.md) | 云模型配置 |
| [PUBLIC_ACCESS_GUIDE.md](PUBLIC_ACCESS_GUIDE.md) | 公网访问配置 |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 故障排除 |

---

## 💡 使用示例

### Web 界面

1. 启动服务：`./start.sh`
2. 访问：http://localhost:6767
3. 配置 API Key
4. 开始聊天

### CLI

```bash
python3 opentalon.py cli
```

---

## 🔧 常用命令

```bash
# 启动 Web 服务
./start.sh

# 停止服务
./stop.sh

# 查看日志
tail -f logs/web.log

# 配置 LLM
python3 configure_llm.py

# 查看配置
python3 opentalon.py configure

# CLI 交互
python3 opentalon.py cli
```

---

## 🛡️ 安全建议

1. **不要提交 API Key**: `.gitignore` 已配置忽略
2. **限制访问 IP**: 在云安全组设置白名单
3. **使用 HTTPS**: 生产环境建议配置 Nginx 反向代理
4. **定期更换 Key**: 在云模型控制台管理

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 📞 联系

- **GitHub**: [opentalon](https://github.com/admin/opentalon)
- **Gitee**: [opentalon](https://gitee.com/admin/opentalon)

---

**🎉 Happy Coding!**
