#!/usr/bin/env python3
"""检查并修复 Qwen 配置"""

import json
from pathlib import Path

config_file = Path.home() / '.opentalon' / 'llm_config.json'

if not config_file.exists():
    print("❌ 配置文件不存在")
    exit(1)

with open(config_file, 'r') as f:
    config = json.load(f)

print("当前配置:")
print(f"  Provider: {config.get('provider', 'unknown')}")
print(f"  API Key: {config.get('api_key', '')[:8]}...")
print(f"  Base URL: {config.get('base_url', '')}")
print(f"  Model: {config.get('model', '')}")
print()

# 检查 Qwen 配置
if 'dashscope' in config.get('base_url', ''):
    print("✅ 检测到通义千问配置")
    print()
    
    # 检查模型
    model = config.get('model', '')
    vision_models = ['qwen-vl', 'qwen-vl-max', 'qwen-vl-plus']
    
    if any(vm in model for vm in vision_models):
        print(f"✅ 模型 {model} 支持视觉识别")
    else:
        print(f"❌ 模型 {model} 不支持视觉识别！")
        print(f"   建议使用：qwen-vl-max 或 qwen-vl-plus")
        print()
        print("正在修复...")
        config['model'] = 'qwen-vl-max'
        print(f"✅ 模型已更新为：qwen-vl-max")
    
    # 检查 Base URL
    base_url = config.get('base_url', '')
    if 'coding.dashscope' in base_url:
        print(f"\n⚠️  注意：compatible-mode 可能不支持图片")
        print(f"   当前：{base_url}")
        print(f"   建议：https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # 保存修复
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 配置已保存到：{config_file}")
    
    # 显示正确的配置说明
    print("\n" + "="*50)
    print("📝 通义千问视觉模型配置说明:")
    print("="*50)
    print("""
1. 获取 API Key:
   https://dashscope.console.aliyun.com/apiKey

2. 正确配置:
   - Provider: dashscope
   - API Key: sk-xxxxxxxx (阿里云 Dashscope Key)
   - Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
   - Model: qwen-vl-max (视觉模型)

3. 测试图片识别:
   - 访问 http://localhost:6767
   - 点击 💬 Chat
   - 点击 📷 上传图片
   - 输入问题并发送
""")
else:
    print("ℹ️  当前不是通义千问配置")
