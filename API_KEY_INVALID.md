# ⚠️ Qwen API Key 无效问题

**问题时间**: 2026-04-12 17:30  
**状态**: ❌ 需要用户重新配置

---

## 🐛 问题诊断

### 当前配置

```json
{
  "provider": "openai",
  "api_key": "sk-sp-0bee5abd4d8e4ae2b023a4060a504add",
  "base_url": "https://coding.dashscope.aliyuncs.com/v1",
  "model": "qwen-vl-max"
}
```

### 问题

1. ❌ **API Key 无效** - 401 错误
2. ❌ **模型已修复** - 从 qwen3.6-plus 改为 qwen-vl-max ✅
3. ⚠️ **Base URL 可能有问题** - 建议使用官方地址

---

## 🔧 解决方案

### 1. 获取正确的 API Key

访问阿里云 Dashscope 控制台：

```
https://dashscope.console.aliyun.com/apiKey
```

步骤：
1. 登录阿里云账号
2. 进入 Dashscope 控制台
3. 点击 "API Key 管理"
4. 创建或复制 API Key（格式：sk-xxxxxxxx）

### 2. 配置 API Key

访问 Web 界面：

```
http://localhost:6767
```

步骤：
1. 点击 **⚙️ Settings**
2. Provider 选择：**Qwen (通义千问)**
3. API Key: 粘贴新的 API Key
4. Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`
5. Model: `qwen-vl-max`
6. 点击 **🔍 Test Connection** 测试
7. 点击 **💾 Save Configuration** 保存

### 3. 测试图片识别

1. 点击 **💬 Chat**
2. 点击 **📷** 上传图片
3. 输入问题："这张图片显示什么？"
4. 点击 **Send**
5. 查看 AI 回复

---

## 📝 正确配置示例

```json
{
  "provider": "dashscope",
  "api_key": "sk-你的新 API Key",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-vl-max",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

---

## 🎯 免费额度

阿里云 Dashscope 提供：

- **新用户**: 免费试用额度
- **qwen-vl-max**: 有一定免费调用次数
- **查看额度**: https://dashscope.console.aliyun.com/overview

---

## 🔍 验证 API Key

运行测试脚本：

```bash
cd /home/admin/projects/opentalon
python3 check_qwen_config.py
```

输出示例：

```
当前配置:
  Provider: dashscope
  API Key: sk-xxxxx...
  Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
  Model: qwen-vl-max

✅ 检测到通义千问配置
✅ 模型 qwen-vl-max 支持视觉识别
```

---

## 📊 其他推荐配置

### Kimi (月之暗面)

```
Provider: Kimi (月之暗面)
API Key: 从 https://platform.moonshot.cn 获取
Base URL: https://api.moonshot.cn/v1
Model: moonshot-v1-128k
```

### OpenAI

```
Provider: OpenAI
API Key: 从 https://platform.openai.com 获取
Base URL: https://api.openai.com/v1
Model: gpt-4o
```

### DeepSeek

```
Provider: DeepSeek
API Key: 从 https://platform.deepseek.com 获取
Base URL: https://api.deepseek.com/v1
Model: deepseek-chat
```

---

## ⚠️ 常见问题

### Q: API Key 格式不对？

A: 不同提供商格式不同：
- 阿里云：`sk-xxxxxxxx`
- OpenAI: `sk-proj-xxxxxxxx` 或 `sk-xxxxxxxx`
- Kimi: `sk-xxxxxxxx`
- DeepSeek: `sk-xxxxxxxx`

### Q: 401 错误？

A: 原因：
1. API Key 无效或过期
2. API Key 未激活
3. 余额不足

解决：
1. 重新获取 API Key
2. 检查账户状态
3. 充值或领取免费额度

### Q: 400 错误？

A: 原因：
1. 模型不支持视觉
2. API 格式错误
3. 图片格式不支持

解决：
1. 使用 qwen-vl-max 模型
2. 使用正确的 API 格式
3. 使用支持的图片格式（JPG/PNG）

---

## 📖 相关文档

- [CLOUD_MODEL_SETUP.md](CLOUD_MODEL_SETUP.md) - 云模型配置指南
- [MULTIMODAL_GUIDE.md](MULTIMODAL_GUIDE.md) - 多模态使用指南
- [QWEN_IMAGE_FIX_COMPLETE.md](QWEN_IMAGE_FIX_COMPLETE.md) - Qwen 图片修复

---

##  获取帮助

1. 检查配置：`python3 check_qwen_config.py`
2. 测试 API: `python3 test_qwen_vision.py`
3. 查看日志：`tail -f logs/web.log`

---

**更新时间**: 2026-04-12 17:30  
**状态**: ⚠️ 需要用户配置新的 API Key
