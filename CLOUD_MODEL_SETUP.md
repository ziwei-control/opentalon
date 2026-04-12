# ⚡ OpenTalon 云模型快速配置指南

**配置文件位置**: `~/.opentalon/llm_config.json`

---

## 🚀 快速开始

### 方式 1: 使用配置工具 (推荐)

```bash
cd /home/admin/projects/opentalon
python3 configure_llm.py
```

按照提示选择云模型提供商并输入 API Key。

### 方式 2: 手动编辑配置文件

```bash
vim ~/.opentalon/llm_config.json
```

---

## ☁️ 支持的云模型提供商

### 1. OpenAI (GPT)

**配置**:
```json
{
  "provider": "openai",
  "api_key": "sk-your-openai-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-3.5-turbo"
}
```

**获取 API Key**: https://platform.openai.com/api-keys

**可用模型**:
- `gpt-4o` - 最新最强
- `gpt-4-turbo` - GPT-4 快速版
- `gpt-3.5-turbo` - 经济实惠

---

### 2. Kimi (月之暗面) 🇨🇳 ⭐ 推荐

**配置**:
```json
{
  "provider": "openai",
  "api_key": "sk-your-kimi-key",
  "base_url": "https://api.moonshot.cn/v1",
  "model": "moonshot-v1-8k"
}
```

**获取 API Key**: https://platform.moonshot.cn/

**可用模型**:
- `moonshot-v1-8k` - 8K 上下文 (Kimi 基础版)
- `moonshot-v1-32k` - 32K 上下文
- `moonshot-v1-128k` - 128K 超长上下文 (Kimi 优势)
- `kimi-latest` - 最新版 (Kimi2.5)
- `kimi-thinking` - 深度思考版

**优势**: 
- ✅ 超长上下文 (128K)
- ✅ 中文能力强
- ✅ 适合长文档分析
- ✅ Kimi2.5 推理能力强

---

### 3. Qwen (通义千问) 🇨🇳 ⭐ 推荐

**配置**:
```json
{
  "provider": "openai",
  "api_key": "sk-your-qwen-key",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-max"
}
```

**获取 API Key**: https://dashscope.console.aliyun.com/

**可用模型**:
- `qwen-max` - 最强模型 (Qwen3.5)
- `qwen-plus` - 平衡版
- `qwen-turbo` - 快速版
- `qwen-long` - 长文本版
- `qwen-coder` - 代码专用

**优势**:
- ✅ 阿里出品，中文优化好
- ✅ Qwen3.5 能力强
- ✅ 代码能力优秀
- ✅ 价格便宜

---

## 🔧 完整配置参数

```json
{
  "provider": "openai",
  "api_key": "sk-your-api-key",
  "base_url": "https://api.xxx.com/v1",
  "model": "model-name",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 60
}
```

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| provider | 提供商类型 | "openai" |
| api_key | API 密钥 | 从官网获取 |
| base_url | API 端点 | 各提供商不同 |
| model | 模型名称 | 根据需求选择 |
| temperature | 创造性 (0-2) | 0.7 (平衡) |
| max_tokens | 最大输出长度 | 4096 |
| timeout | 超时时间 (秒) | 60 |

---

## ✅ 验证配置

### 1. 查看配置状态

```bash
cd /home/admin/projects/opentalon
python3 opentalon.py config
```

### 2. 测试连接

```bash
python3 configure_llm.py
# 选择 "测试连接" 选项
```

### 3. 启动 CLI 测试

```bash
python3 opentalon.py cli
```

输入一个问题测试是否正常工作。

---

## 💰 价格对比 (参考)

| 提供商 | 模型 | 输入价格 | 输出价格 | 特点 |
|--------|------|---------|---------|------|
| OpenAI | gpt-3.5-turbo | $0.5/M | $1.5/M | 便宜快速 |
| OpenAI | gpt-4o | $5/M | $15/M | 最强 |
| DeepSeek | deepseek-chat | ¥1/M | ¥2/M | 性价比高 |
| Moonshot | moonshot-v1-8k | ¥12/M | ¥12/M | 长上下文 |
| Zhipu | glm-4 | ¥0.1/K | ¥0.1/K | 中文好 |
| Qwen | qwen-max | ¥40/M | ¥120/M | 阿里出品 |

*注：价格可能有变动，请以官网为准*

---

## 🔒 安全提示

1. **保护 API Key**
   - 不要提交到 Git
   - 不要分享给他人
   - 定期轮换

2. **使用环境变量** (可选)
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

3. **设置使用限额**
   - 在提供商控制台设置月度预算
   - 监控使用情况

---

## 🛠️ 故障排除

### ❌ 401 Unauthorized

**原因**: API Key 无效或过期  
**解决**: 
1. 检查 API Key 是否正确
2. 确认账户有余额
3. 重新生成 API Key

### ❌ 404 Not Found

**原因**: 模型名称错误或端点不对  
**解决**:
1. 检查 model 名称
2. 检查 base_url 是否正确

### ❌ Connection Timeout

**原因**: 网络问题或服务不可用  
**解决**:
1. 检查网络连接
2. 增加 timeout 值
3. 尝试其他提供商

### ❌ Rate Limit Exceeded

**原因**: 请求频率超限  
**解决**:
1. 降低请求频率
2. 升级账户套餐
3. 增加 timeout 值

---

## 📞 获取帮助

- **文档**: `/home/admin/projects/opentalon/LLM_CONFIG_GUIDE.md`
- **配置工具**: `python3 configure_llm.py`
- **项目 README**: `/home/admin/projects/opentalon/README.md`

---

**更新时间**: 2026-04-09  
**版本**: v0.2.0
