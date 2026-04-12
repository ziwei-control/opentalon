---
# OpenTalon LLM 配置指南
# 配置你的智能体大脑
---

## 📍 配置文件位置

**Linux/macOS**: `~/.opentalon/llm_config.json`  
**Windows**: `%USERPROFILE%\.opentalon\llm_config.json`

---

## ⚡ 快速配置

### 方案 1: OpenAI (默认)

```json
{
  "provider": "openai",
  "api_key": "sk-your-api-key-here",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 60
}
```

### 方案 2: Ollama (本地模型)

```json
{
  "provider": "ollama",
  "base_url": "http://localhost:11434",
  "model": "llama2",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 120
}
```

### 方案 3: LM Studio (本地模型)

```json
{
  "provider": "lmstudio",
  "base_url": "http://localhost:1234/v1",
  "model": "local-model",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 120
}
```

### 方案 4: 其他 OpenAI 兼容 API

```json
{
  "provider": "openai",
  "api_key": "your-api-key",
  "base_url": "https://api.deepseek.com/v1",
  "model": "deepseek-chat",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 60
}
```

---

## 🔑 获取 API Key

### OpenAI

1. 访问 https://platform.openai.com/api-keys
2. 创建新的 API Key
3. 复制到配置文件中

### DeepSeek

1. 访问 https://platform.deepseek.com/
2. 注册并获取 API Key
3. 使用 base_url: `https://api.deepseek.com/v1`

### Moonshot

1. 访问 https://platform.moonshot.cn/
2. 获取 API Key
3. 使用 base_url: `https://api.moonshot.cn/v1`

---

## 🏠 本地模型配置

### Ollama

1. 安装 Ollama: https://ollama.ai/
2. 下载模型: `ollama pull llama2`
3. 启动服务: `ollama serve`
4. 配置如上所示

### LM Studio

1. 下载 LM Studio: https://lmstudio.ai/
2. 下载模型
3. 启动本地服务器
4. 配置如上所示

---

## ✅ 验证配置

```bash
cd /home/admin/projects/opentalon
python3 opentalon.py config
```

如果配置正确，会显示:
```
✅ LLM 配置：已加载
   Provider: openai
   Model: gpt-3.5-turbo
```

---

## 🔒 安全提示

- ⚠️ **不要** 将 API Key 提交到版本控制
- ✅ 使用环境变量: `export OPENAI_API_KEY=sk-...`
- ✅ 本地模型不需要 API Key，更安全
- ✅ 定期轮换 API Key

---

## 📊 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| provider | LLM 提供商 (openai/ollama/lmstudio) | openai |
| api_key | API 密钥 | 空 (从环境变量读取) |
| base_url | API 端点 | https://api.openai.com/v1 |
| model | 模型名称 | gpt-3.5-turbo |
| temperature | 温度 (0-2，越高越随机) | 0.7 |
| max_tokens | 最大输出长度 | 4096 |
| timeout | 请求超时 (秒) | 60 |

---

## 🛠️ 故障排除

### 问题：401 Unauthorized

**原因**: API Key 无效或过期  
**解决**: 检查 API Key 是否正确，是否已过期

### 问题：Connection refused

**原因**: 本地模型服务未启动  
**解决**: 启动 Ollama 或 LM Studio 服务

### 问题：Model not found

**原因**: 模型名称错误或未下载  
**解决**: 检查模型名称，下载对应模型

---

## 📝 示例配置目录

```
~/.opentalon/
├── llm_config.json      # LLM 配置
├── cli_history          # CLI 历史记录
└── logs/                # 日志目录
```

---

**创建时间**: 2026-04-09  
**版本**: 0.1.0
