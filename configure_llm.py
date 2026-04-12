#!/usr/bin/env python3
"""
OpenTalon LLM 配置工具
快速配置云模型提供商
"""

import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / '.opentalon' / 'llm_config.json'

# 云模型提供商预设
PROVIDERS = {
    '1': {
        'name': 'OpenAI (GPT)',
        'provider': 'openai',
        'base_url': 'https://api.openai.com/v1',
        'models': ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        'website': 'https://platform.openai.com'
    },
    '2': {
        'name': 'DeepSeek (深度求索)',
        'provider': 'openai',
        'base_url': 'https://api.deepseek.com/v1',
        'models': ['deepseek-chat', 'deepseek-coder'],
        'website': 'https://platform.deepseek.com'
    },
    '3': {
        'name': 'Moonshot (月之暗面)',
        'provider': 'openai',
        'base_url': 'https://api.moonshot.cn/v1',
        'models': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
        'website': 'https://platform.moonshot.cn'
    },
    '4': {
        'name': 'Zhipu (智谱 AI)',
        'provider': 'openai',
        'base_url': 'https://open.bigmodel.cn/api/paas/v4',
        'models': ['glm-4', 'glm-3-turbo'],
        'website': 'https://open.bigmodel.cn'
    },
    '5': {
        'name': 'Baichuan (百川智能)',
        'provider': 'openai',
        'base_url': 'https://api.baichuan-ai.com/v1',
        'models': ['Baichuan4', 'Baichuan3-Turbo'],
        'website': 'https://platform.baichuan-ai.com'
    },
    '6': {
        'name': 'Qwen (通义千问)',
        'provider': 'openai',
        'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'models': ['qwen-max', 'qwen-plus', 'qwen-turbo'],
        'website': 'https://dashscope.console.aliyun.com'
    },
    '7': {
        'name': '自定义 OpenAI 兼容 API',
        'provider': 'openai',
        'base_url': 'custom',
        'models': [],
        'website': ''
    }
}

def print_banner():
    print("""
    ╔═══════════════════════════════════════╗
    ║    OpenTalon LLM 配置工具              ║
    ║        配置你的云模型大脑              ║
    ╚═══════════════════════════════════════╝
    """)

def list_providers():
    print("\n请选择云模型提供商:\n")
    for key, info in PROVIDERS.items():
        print(f"  {key}. {info['name']}")
        print(f"     端点：{info['base_url']}")
        print(f"     模型：{', '.join(info['models']) if info['models'] else '自定义'}")
        print(f"     网站：{info['website']}")
        print()

def get_api_key(provider_name):
    print(f"\n请输入你的 {provider_name} API Key:")
    print("💡 提示：API Key 通常以 'sk-' 开头")
    print("💡 可以在提供商官网的控制台获取")
    print("")
    
    while True:
        api_key = input("API Key: ").strip()
        if api_key:
            return api_key
        print("❌ API Key 不能为空，请重新输入")

def get_custom_url():
    print("\n请输入自定义 API 端点 (base_url):")
    print("例如：https://your-api.com/v1")
    print("")
    
    while True:
        url = input("Base URL: ").strip()
        if url:
            return url
        print("❌ 端点不能为空")

def get_custom_model():
    print("\n请输入模型名称:")
    print("例如：gpt-4, llama-2, 或你的自定义模型名")
    print("")
    
    while True:
        model = input("Model: ").strip()
        if model:
            return model
        print("❌ 模型名称不能为空")

def save_config(config):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 配置已保存到：{CONFIG_FILE}")

def test_connection(config):
    print("\n🔍 测试连接...")
    
    try:
        from core.llm_client import create_llm_client
        
        os.chdir('/home/admin/projects/opentalon')
        client = create_llm_client(str(CONFIG_FILE))
        
        print(f"✅ LLM 客户端创建成功")
        print(f"   Provider: {config['provider']}")
        print(f"   Model: {config['model']}")
        print(f"   Base URL: {config['base_url']}")
        
        # 简单测试
        print("\n📝 发送测试消息...")
        response = client.chat([
            {"role": "user", "content": "Hello, this is a test. Reply with 'OK' only."}
        ])
        
        if response and not response.startswith("❌"):
            print(f"✅ 连接测试成功！响应：{response[:50]}...")
            return True
        else:
            print(f"⚠️  连接测试失败：{response}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
        return False

def main():
    print_banner()
    
    # 检查现有配置
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            current_config = json.load(f)
        
        print(f"📁 检测到现有配置:")
        print(f"   Provider: {current_config.get('provider', 'unknown')}")
        print(f"   Model: {current_config.get('model', 'unknown')}")
        print(f"   Base URL: {current_config.get('base_url', 'unknown')}")
        print("")
        
        choice = input("是否修改配置？(y/n): ").strip().lower()
        if choice != 'y':
            print("👋 保持现有配置，退出。")
            return
    
    # 选择提供商
    list_providers()
    
    while True:
        choice = input("选择提供商编号 (1-7): ").strip()
        if choice in PROVIDERS:
            break
        print("❌ 无效选择，请输入 1-7 之间的数字")
    
    provider_info = PROVIDERS[choice]
    
    # 获取 API Key
    api_key = get_api_key(provider_info['name'])
    
    # 配置
    config = {
        'provider': provider_info['provider'],
        'api_key': api_key,
        'base_url': provider_info['base_url'],
        'model': provider_info['models'][0] if provider_info['models'] else '',
        'temperature': 0.7,
        'max_tokens': 4096,
        'timeout': 60
    }
    
    # 处理自定义
    if provider_info['base_url'] == 'custom':
        config['base_url'] = get_custom_url()
        config['model'] = get_custom_model()
    elif provider_info['models']:
        print(f"\n选择模型 (直接回车使用默认 '{config['model']}'):")
        for i, model in enumerate(provider_info['models'], 1):
            print(f"  {i}. {model}")
        
        model_choice = input(f"\n模型选择 (1-{len(provider_info['models'])}): ").strip()
        if model_choice.isdigit() and 1 <= int(model_choice) <= len(provider_info['models']):
            config['model'] = provider_info['models'][int(model_choice) - 1]
    
    # 保存配置
    save_config(config)
    
    # 测试连接
    test_choice = input("\n是否测试连接？(y/n): ").strip().lower()
    if test_choice == 'y':
        test_connection(config)
    
    print("\n✅ 配置完成！")
    print("\n现在可以使用 OpenTalon:")
    print("  cd /home/admin/projects/opentalon")
    print("  python3 opentalon.py cli")

if __name__ == "__main__":
    main()
