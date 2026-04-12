#!/usr/bin/env python3
"""测试 Qwen 图片识别 API"""

import requests
import base64
import json

# 读取配置
with open('/home/admin/.opentalon/llm_config.json', 'r') as f:
    config = json.load(f)

api_key = config.get('api_key', '')
print(f"使用 API Key: {api_key[:8]}...")

# 创建测试图片（简单的 base64）
# 这里用一个真实的图片 URL 代替
image_url = "https://www.example.com/test.jpg"

# 测试 Qwen 原生 API
url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# 使用图片 URL 测试
payload = {
    'model': 'qwen-vl-max',
    'input': {
        'messages': [{
            'role': 'user',
            'content': [
                {'image': 'https://img.alicdn.com/imgextra/i2/O1CN01YXzLxH1MbFQvJKdWZ_!!6000000001455-0-tps-1024-1024.jpg'},  # 熊猫图片示例
                {'text': '这张图片显示的是什么？'}
            ]
        }]
    },
    'parameters': {
        'temperature': 0.7,
        'max_tokens': 2048
    }
}

print(f"\n发送请求到：{url}")
print(f"模型：qwen-vl-max")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    print(f"\n状态码：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 请求成功！")
        print("\n响应内容:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 提取回复
        try:
            content = result['output']['choices'][0]['message']['content']
            print(f"\n📝 AI 回复：{content}")
        except Exception as e:
            print(f"解析回复失败：{e}")
    else:
        print(f"❌ 请求失败：{response.status_code}")
        print(f"错误信息：{response.text}")
        
except Exception as e:
    print(f"❌ 异常：{e}")
