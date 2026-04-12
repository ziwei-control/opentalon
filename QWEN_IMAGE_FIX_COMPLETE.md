# ✅ 修复图片识别 400 错误

**完成时间**: 2026-04-12 17:05  
**版本**: v0.4.4  
**状态**: ✅ 已修复并同步

---

## 🐛 问题现象

用户上传熊猫图片并问"这显示的什么"，出现错误：

```
❌ 请求失败：400 Client Error: Bad Request
for url: https://coding.dashscope.aliyuncs.com/v1/chat/completions
```

---

## 🔍 问题原因

**通义千问（Qwen）的 API 格式与 OpenAI 不同！**

### OpenAI 格式（错误）

```python
{
    'role': 'user',
    'content': [
        {'type': 'text', 'text': '请描述这张图片'},
        {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,...'}}
    ]
}
```

### Qwen 格式（正确）

```python
{
    'role': 'user',
    'content': [
        {'image': 'data:image/png;base64,...'},  # ✅ 直接使用 image 键
        {'text': '请描述这张图片'}
    ]
}
```

---

## 🔧 修复内容

### 1. 修复 web_server.py 聊天 API

```python
# 构建消息
if image_data:
    # 通义千问需要特殊格式
    if 'dashscope' in base_url:
        # Qwen 格式：图片作为单独的消息部分
        messages = [{
            'role': 'user',
            'content': [
                {'image': image_data},  # ✅ Qwen 直接使用 base64
                {'text': message or '请描述这张图片'}
            ]
        }]
        model = 'qwen-vl-max'
    else:
        # OpenAI/Kimi 格式
        messages = [{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': message or '请描述这张图片'},
                {'type': 'image_url', 'image_url': {'url': image_data}}
            ]
        }]
```

### 2. 修复 multimodal.py 多模态 API

```python
# 构建消息
if 'dashscope' in base_url:
    # Qwen 格式
    messages = [{
        'role': 'user',
        'content': [
            {'image': f'data:{mime_type};base64,{base64_image}'},
            {'text': prompt}
        ]
    }]
    model = 'qwen-vl-max'
else:
    # OpenAI/Kimi 格式
    messages = [{
        'role': 'user',
        'content': [
            {'type': 'text', 'text': prompt},
            {
                'type': 'image_url',
                'image_url': {
                    'url': f'data:{mime_type};base64,{base64_image}'
                }
            }
        ]
    }]
```

---

## 📊 API 格式对比

| 提供商 | 图片格式 | 模型 |
|--------|----------|------|
| **Qwen** | `{'image': base64}` | qwen-vl-max |
| **OpenAI** | `{'type': 'image_url', 'image_url': {'url': data:...}}` | gpt-4o |
| **Kimi** | `{'type': 'image_url', 'image_url': {'url': data:...}}` | moonshot-v1-128k |

---

## ✅ 验证结果

### 服务状态

```bash
$ ps aux | grep web_server.py
admin python3 web_server.py --port 6767 ✅

$ curl http://localhost:6767
pandaco.asia ✅
```

### 功能测试

1. **聊天 + 图片** ✅ - 上传图片并提问正常
2. **多模态图片识别** ✅ - 图片分析正常
3. **纯文字聊天** ✅ - 文字消息正常
4. **配置保存** ✅ - API Key 设置正常

---

## 🎯 使用指南

### 使用 Qwen 识别图片

1. **配置 Qwen API**
   - 访问 http://localhost:6767
   - 点击 ⚙️ Settings
   - Provider: Qwen (通义千问)
   - API Key: 你的 Dashscope API Key
   - Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
   - Model: qwen-vl-max（自动设置）
   - 保存配置

2. **上传图片**
   - 点击 💬 Chat
   - 点击 📷 按钮选择图片
   - 输入问题："这显示的是什么？"
   - 点击 Send

3. **查看结果**
   - AI 会分析图片并回复
   - 例如："这是一张熊猫的图片..."

---

## 📝 测试案例

### 案例 1: 熊猫图片

**用户**: "这显示的是什么" + 🐼 图片

**预期回复**:
```
这是一张熊猫的图片。图片显示了一个简化的熊猫头像，
有黑色的耳朵、眼圈和鼻子，背景是白色的。
```

### 案例 2: 截图 OCR

**用户**: "提取图中的文字" + 📄 截图

**预期回复**:
```
图中的文字是：
"Hello World"
...
```

### 案例 3: 代码截图

**用户**: "这段代码有什么问题？" + 💻 代码截图

**预期回复**:
```
这段代码存在以下问题：
1. 缺少错误处理
2. 变量命名不规范
...
```

---

## 🌐 支持的云模型

### 图片识别推荐

| 提供商 | 模型 | 价格 | 效果 |
|--------|------|------|------|
| **Qwen** | qwen-vl-max | 💰 | ⭐⭐⭐⭐⭐ |
| **OpenAI** | gpt-4o | 💰💰 | ⭐⭐⭐⭐⭐ |
| **Kimi** | moonshot-v1-128k | 💰 | ⭐⭐⭐⭐ |

### 文字聊天推荐

| 提供商 | 模型 | 价格 | 效果 |
|--------|------|------|------|
| **Kimi** | kimi-latest | 💰 | ⭐⭐⭐⭐⭐ |
| **Qwen** | qwen-max | 💰 | ⭐⭐⭐⭐ |
| **DeepSeek** | deepseek-chat | 💰 | ⭐⭐⭐⭐ |

---

## 📊 Git 提交

```
666c2a0 fix: 修复通义千问图片识别 400 错误
ad38ab1 docs: 添加 requests 模块修复文档
6eca665 fix: 修复 requests 模块未定义错误
```

---

## 🌐 仓库同步

| 平台 | 状态 | 地址 |
|------|------|------|
| **GitHub** | ✅ | https://github.com/ziwei-control/opentalon |
| **Gitee** | ✅ | https://gitee.com/pandac0/opentalon |

---

## 📁 文件变更

| 文件 | 变更 | 说明 |
|------|------|------|
| `web_server.py` | +28 -14 行 | 修复 Qwen 图片格式 |
| `core/multimodal.py` | +23 -14 行 | 修复 Qwen 图片格式 |

---

## ⚠️ 注意事项

### API Key 获取

- **Qwen**: https://dashscope.console.aliyun.com/apiKey
- **Kimi**: https://platform.moonshot.cn/console/api-keys
- **OpenAI**: https://platform.openai.com/api-keys

### 免费额度

- **Qwen**: 新用户有免费额度
- **Kimi**: 每月有免费额度
- **OpenAI**: 新用户有$5 免费额度

### 图片大小

- 建议 < 10MB
- 格式：JPG, PNG, GIF, WebP
- 分辨率：建议 < 4096x4096

---

## 📖 相关文档

- [README.md](README.md) - 项目总览
- [MULTIMODAL_GUIDE.md](MULTIMODAL_GUIDE.md) - 多模态指南
- [CLOUD_MODEL_SETUP.md](CLOUD_MODEL_SETUP.md) - 云模型配置
- [BLACK_THEME_COMPLETE.md](BLACK_THEME_COMPLETE.md) - 黑色主题

---

## 🎉 总结

OpenTalon v0.4.4 修复了图片识别问题：

1. ✅ **Qwen 格式修复** - 使用正确的 API 格式
2. ✅ **多模态支持** - 聊天和多模态标签都支持
3. ✅ **自动模型切换** - 自动使用 qwen-vl-max
4. ✅ **向后兼容** - OpenAI/Kimi 格式保持不变

**现在可以正常识别图片了！** 🎉

**仓库已同步**:
- GitHub: https://github.com/ziwei-control/opentalon ✅
- Gitee: https://gitee.com/pandac0/opentalon ✅

---

**版本**: v0.4.4  
**完成时间**: 2026-04-12 17:05  
**状态**: ✅ 已修复并同步
