# 🖼️ OpenTalon 多模态功能指南

**更新时间**: 2026-04-12  
**版本**: v0.4.0

---

## 🎉 新增功能

OpenTalon 现在支持多模态交互：

1. **🖼️ 图片识别** - 上传图片，AI 帮你识别和分析
2. **🎤 音频识别** - 上传音频，AI 转录文字并回应
3. **📊 文件管理** - 查看上传统计，清理旧文件

---

## 🖼️ 图片识别

### 支持的格式

- JPG / JPEG
- PNG
- GIF
- WebP

### 使用方法

#### Web 界面

1. 访问 `http://localhost:6767`
2. 点击 **🖼️ 多模态** 标签
3. 选择 **🖼️ 图片识别**
4. 点击或拖拽上传图片
5. 输入识别提示词（可选）
6. 查看识别结果

#### API 调用

```bash
curl -X POST http://localhost:6767/api/upload/image \
  -F "file=@/path/to/image.jpg" \
  -F "prompt=请描述这张图片"
```

**响应示例**:
```json
{
  "success": true,
  "filename": "20260412_120000_test.jpg",
  "path": "/home/admin/.opentalon/uploads/image/20260412_120000_test.jpg",
  "result": "这是一张美丽的风景照片..."
}
```

### 支持的模型

| 提供商 | 视觉模型 |
|--------|---------|
| OpenAI | gpt-4o, gpt-4-turbo, gpt-4-vision |
| Kimi | moonshot-v1-128k |
| Qwen | qwen-vl-max |
| Claude | claude-3 |

---

## 🎤 音频识别

### 支持的格式

- MP3
- WAV
- OGG
- M4A
- FLAC
- AAC

### 使用方法

#### Web 界面

1. 访问 `http://localhost:6767`
2. 点击 **🖼️ 多模态** 标签
3. 选择 **🎤 音频识别**
4. 点击或拖拽上传音频
5. 输入额外提示（可选）
6. 查看转录文字和 AI 回应

#### API 调用

```bash
curl -X POST http://localhost:6767/api/upload/audio \
  -F "file=@/path/to/audio.mp3" \
  -F "prompt=请总结这段语音"
```

**响应示例**:
```json
{
  "success": true,
  "filename": "20260412_120000_voice.mp3",
  "path": "/home/admin/.opentalon/uploads/audio/20260412_120000_voice.mp3",
  "transcription": "你好，我想了解一下今天的天气。",
  "response": "根据语音内容，用户想了解今天的天气情况..."
}
```

### 语音识别要求

⚠️ **重要**: 语音识别功能需要 **OpenAI API**

- 使用 OpenAI Whisper API 进行转录
- 其他提供商暂不支持语音识别
- 建议使用 OpenAI API Key 配置

---

## 📊 文件管理

### 查看统计

访问 **🖼️ 多模态** → **📊 统计** 查看：

- 上传图片数量
- 上传音频数量
- 总占用空间

### 清理旧文件

```bash
curl -X POST http://localhost:6767/api/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

**响应示例**:
```json
{
  "success": true,
  "cleaned": 15
}
```

### 上传目录

文件保存在：`~/.opentalon/uploads/`

```
~/.opentalon/uploads/
├── image/
│   ├── 20260412_120000_test.jpg
│   └── ...
└── audio/
    ├── 20260412_120000_voice.mp3
    └── ...
```

---

## 🔧 配置要求

### 图片识别配置

#### OpenAI (推荐)

```json
{
  "provider": "openai",
  "api_key": "sk-...",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4o"
}
```

#### Kimi

```json
{
  "provider": "moonshot",
  "api_key": "sk-...",
  "base_url": "https://api.moonshot.cn/v1",
  "model": "moonshot-v1-128k"
}
```

#### Qwen

```json
{
  "provider": "dashscope",
  "api_key": "sk-...",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-vl-max"
}
```

### 音频识别配置

⚠️ **仅支持 OpenAI**

```json
{
  "provider": "openai",
  "api_key": "sk-...",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4o"
}
```

---

## 💡 使用场景

### 图片识别场景

1. **图片描述** - "请描述这张图片"
2. **OCR 文字识别** - "提取图片中的文字"
3. **物体检测** - "图片中有哪些物体？"
4. **场景分析** - "这是什么场景？"
5. **情感分析** - "这张图片传达什么情感？"
6. **代码截图转代码** - "将截图中的代码提取出来"
7. **图表分析** - "分析这个图表的数据"

### 音频识别场景

1. **会议记录** - 上传会议录音，自动生成纪要
2. **语音笔记** - 语音转文字，AI 整理要点
3. **采访转录** - 采访录音转文字稿
4. **语音指令** - 语音控制，AI 执行任务
5. **播客摘要** - 上传播客，AI 总结内容

---

## 🐛 故障排除

### 问题 1: 图片识别失败

**错误**: "无法读取图片"

**解决**:
- 检查图片格式是否支持
- 检查图片文件是否损坏
- 确认上传目录有写入权限

### 问题 2: 音频识别失败

**错误**: "当前提供商不支持语音识别"

**解决**:
- 使用 OpenAI API Key
- 配置 model 为 gpt-4o 或其他 OpenAI 模型

### 问题 3: 上传文件大小限制

**错误**: "文件太大"

**解决**:
- 图片建议 < 10MB
- 音频建议 < 25MB
- 压缩文件后重新上传

### 问题 4: API 调用失败

**错误**: "请求失败：401 Unauthorized"

**解决**:
- 检查 API Key 是否正确
- 检查 API Key 是否有足够余额
- 确认模型名称正确

---

## 📊 API 参考

### 上传图片

```
POST /api/upload/image
Content-Type: multipart/form-data

参数:
- file: 图片文件 (必需)
- prompt: 识别提示词 (可选，默认："请描述这张图片")

响应:
{
  "success": true/false,
  "filename": "文件名",
  "path": "文件路径",
  "result": "识别结果",
  "error": "错误信息"
}
```

### 上传音频

```
POST /api/upload/audio
Content-Type: multipart/form-data

参数:
- file: 音频文件 (必需)
- prompt: 额外提示 (可选)

响应:
{
  "success": true/false,
  "filename": "文件名",
  "path": "文件路径",
  "transcription": "转录文字",
  "response": "AI 回应",
  "error": "错误信息"
}
```

### 获取统计

```
GET /api/stats

响应:
{
  "success": true,
  "stats": {
    "images": 10,
    "audio": 5,
    "total_size": 12345678
  },
  "supported_images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
  "supported_audio": [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"]
}
```

### 清理文件

```
POST /api/cleanup
Content-Type: application/json

参数:
- days: 清理多少天前的文件 (可选，默认：7)

响应:
{
  "success": true,
  "cleaned": 15
}
```

---

## 🔐 隐私与安全

### 数据存储

- 所有上传文件保存在本地 (`~/.opentalon/uploads/`)
- 不会自动上传到云端
- 定期清理旧文件

### API Key 安全

- API Key 只保存在本地 (`~/.opentalon/llm_config.json`)
- 不会发送到 OpenTalon 服务器
- 仅用于调用 LLM 提供商 API

### 建议

1. 定期清理上传文件
2. 不要分享 API Key
3. 使用 HTTPS 访问（生产环境）
4. 配置防火墙限制访问

---

## 📝 示例代码

### Python 上传图片

```python
import requests

url = 'http://localhost:6767/api/upload/image'
files = {'file': open('test.jpg', 'rb')}
data = {'prompt': '请描述这张图片'}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Python 上传音频

```python
import requests

url = 'http://localhost:6767/api/upload/audio'
files = {'file': open('voice.mp3', 'rb')}
data = {'prompt': '请总结这段语音'}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### JavaScript 上传图片

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('prompt', '请描述这张图片');

fetch('/api/upload/image', {
  method: 'POST',
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## 🎯 最佳实践

### 图片识别

1. **清晰的提示词** - 明确告诉 AI 你想要什么
2. **合适的图片大小** - 不要太大（<10MB）也不要太小
3. **正确的格式** - 使用 JPG 或 PNG 获得最佳兼容性

### 音频识别

1. **清晰的录音** - 减少背景噪音
2. **标准格式** - 使用 MP3 或 WAV
3. **合理长度** - 建议 < 10 分钟

### 文件管理

1. **定期清理** - 每周清理一次旧文件
2. **分类存储** - 图片和音频自动分开
3. **备份重要文件** - 重要的上传文件及时备份

---

## 📞 需要帮助？

### 文档

- [README.md](README.md) - 项目总览
- [DEPLOY.md](DEPLOY.md) - 部署指南
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [MULTIMODAL_GUIDE.md](MULTIMODAL_GUIDE.md) - 本文档

### 常见问题

- 图片识别失败 → 检查模型是否支持视觉
- 音频识别失败 → 使用 OpenAI API
- 上传失败 → 检查文件大小和格式

---

**最后更新**: 2026-04-12  
**版本**: v0.4.0
