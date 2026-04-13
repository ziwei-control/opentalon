#!/usr/bin/env python3
"""
OpenTalon Web 界面 (黑色主题版)
支持：
- 黑色主题 UI
- 聊天框直接上传图片
- 图片识别和提问
- 亮绿色文字配色
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入多模态模块
from core.multimodal import (
    save_uploaded_file,
    analyze_image,
    process_audio_message,
    get_upload_stats,
    cleanup_old_files,
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_AUDIO_FORMATS
)

# 导入搜索模块
from core.search import search_web, search_news, fetch_webpage_content, get_realtime_context

app = Flask(__name__)
CORS(app)

# 配置文件路径
CONFIG_FILE = Path.home() / '.opentalon' / 'llm_config.json'

# 加载配置
def load_llm_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# 保存配置
def save_llm_config(config):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return True

# 简单的 LLM 调用
def call_llm(messages):
    config = load_llm_config()
    if not config:
        return "❌ LLM 未配置，请在网页设置中配置 API Key"
    
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', 'https://api.openai.com/v1')
    model = config.get('model', 'gpt-3.5-turbo')
    
    url = f"{base_url}/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model,
        'messages': messages,
        'temperature': config.get('temperature', 0.7),
        'max_tokens': config.get('max_tokens', 4096)
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ 请求失败：{str(e)}"


# ==================== API 路由 ====================

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    config = load_llm_config()
    if config:
        # 返回完整配置（本地存储，不需要隐藏）
        return jsonify({'success': True, 'config': config})
    return jsonify({'success': False, 'config': {}})


@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置"""
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '无效数据'})
    
    # 验证必要字段
    if 'api_key' not in data or not data['api_key']:
        return jsonify({'success': False, 'error': 'API Key 不能为空'})
    
    # 加载现有配置（保留其他字段）
    existing_config = load_llm_config() or {}
    
    # 合并配置（用户提供的覆盖现有的）
    merged_config = {**existing_config, **data}
    
    # 保存配置
    save_llm_config(merged_config)
    
    # 测试连接
    test_result = test_llm_connection(merged_config)
    
    return jsonify({
        'success': True,
        'message': '配置已保存并固化',
        'test_result': test_result
    })


@app.route('/api/config/test', methods=['POST'])
def test_config():
    """测试配置"""
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '无效数据'})
    
    result = test_llm_connection(data)
    return jsonify(result)


@app.route('/api/chat', methods=['POST'])
def chat():
    """文字聊天（支持带图片和实时联网搜索）"""
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '消息不能为空'})
    
    message = data.get('message', '')
    image_data = data.get('image', None)  # base64 图片数据
    
    config = load_llm_config()
    if not config:
        return jsonify({'success': False, 'error': 'LLM 未配置'})
    
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', 'https://api.openai.com/v1')
    model = config.get('model', 'gpt-3.5-turbo')
    
    # 智能检测是否需要联网搜索
    search_keywords = [
        # 时间相关
        '今天', 'today', '现在', 'now', '当前', 'current', '最新', 'latest',
        '刚刚', 'just', '最近', 'recent', '实时', 'real-time',
        # 新闻热点
        '新闻', 'news', '热点', 'hot', '头条', 'headline', '事件', 'event',
        # 版本信息
        '版本', 'version', '更新', 'update', '发布', 'release',
        # 天气
        '天气', 'weather', '气温', 'temperature', '下雨', 'rain', '晴天', 'sunny',
        # 金融
        '股票', 'stock', '价格', 'price', '汇率', 'rate', '币价', 'crypto',
        '比特币', 'bitcoin', 'BTC', '以太坊', 'ethereum', 'ETH',
        # 搜索意图
        '搜索', 'search', '查找', 'find', '查询', 'query', '了解', 'learn',
        # 体育
        '比赛', 'match', '比分', 'score', '球队', 'team',
        # 其他实时信息
        '疫情', 'pandemic', '选举', 'election', '战争', 'war'
    ]
    
    # 检测是否需要搜索
    need_search = any(kw in message.lower() or kw in message for kw in search_keywords) and not image_data
    
    # 调试日志
    print(f"\n💬 用户消息：{message[:100]}...")
    print(f"🔍 检测关键词：{need_search}")
    
    # 如果需要搜索，获取实时信息
    search_context = ""
    search_status = "disabled"
    if need_search:
        try:
            print("🌐 开始实时搜索...")
            search_status = "searching"
            
            # 获取实时上下文
            search_context = get_realtime_context(message, max_results=5)
            
            print(f"✅ 搜索完成，获取到上下文信息")
            search_status = "completed"
            
        except Exception as e:
            print(f"❌ 搜索错误：{e}")
            search_context = f"\n\n⚠️ 搜索暂时不可用：{str(e)}"
            search_status = "error"
    
    # 构建消息（带搜索上下文）
    if image_data:
        # 有图片，使用视觉模型
        if 'dashscope' in base_url:
            url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': 'qwen-vl-max',
                'input': {
                    'messages': [{
                        'role': 'user',
                        'content': [
                            {'image': image_data},
                            {'text': message or '请描述这张图片'}
                        ]
                    }]
                },
                'parameters': {
                    'temperature': config.get('temperature', 0.7),
                    'max_tokens': config.get('max_tokens', 4096)
                }
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                result = response.json()
                content = result['output']['choices'][0]['message']['content']
                return jsonify({'success': True, 'response': content, 'search_status': 'disabled'})
            except Exception as e:
                return jsonify({'success': False, 'error': f'请求失败：{str(e)}'})
        else:
            messages = [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': message or '请描述这张图片'},
                    {'type': 'image_url', 'image_url': {'url': image_data}}
                ]
            }]
            
            vision_models = ['gpt-4o', 'gpt-4-turbo', 'gpt-4-vision', 'qwen-vl', 'claude-3']
            if not any(vm in model.lower() for vm in vision_models):
                if 'moonshot' in base_url:
                    model = 'moonshot-v1-128k'
                elif 'openai' in base_url:
                    model = 'gpt-4o'
    else:
        # 纯文字（带搜索上下文）
        if search_context:
            system_prompt = """你是一个智能助手，可以访问实时互联网信息。
请根据提供的实时搜索结果回答用户的问题。
如果搜索结果中有相关信息，请优先引用并标注来源。
如果搜索结果不足，请基于你的知识回答，并说明哪些是实时信息，哪些是你的知识。
回答要准确、简洁、有帮助。"""
            
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"{message}{search_context}\n\n请根据以上实时信息回答用户的问题。"}
            ]
        else:
            messages = [{'role': 'user', 'content': message}]
    
    # 调用 LLM
    if not image_data or 'dashscope' not in base_url:
        url = f"{base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': model,
            'messages': messages,
            'temperature': config.get('temperature', 0.7),
            'max_tokens': config.get('max_tokens', 4096)
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            result = data['choices'][0]['message']['content']
            return jsonify({
                'success': True, 
                'response': result,
                'search_status': search_status,
                'has_search': need_search
            })
        except Exception as e:
            return jsonify({'success': False, 'error': f'请求失败：{str(e)}'})


@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    """上传图片并识别"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '未选择文件'})
    
    file = request.files['file']
    prompt = request.form.get('prompt', '请描述这张图片')
    
    # 保存文件
    save_result = save_uploaded_file(file, 'image')
    if not save_result['success']:
        return jsonify(save_result)
    
    # 识别图片
    analyze_result = analyze_image(save_result['path'], prompt)
    
    return jsonify({
        'success': analyze_result['success'],
        'filename': save_result['filename'],
        'path': save_result['path'],
        'result': analyze_result.get('result', ''),
        'error': analyze_result.get('error', '')
    })


@app.route('/api/upload/audio', methods=['POST'])
def upload_audio():
    """上传音频并识别"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '未选择文件'})
    
    file = request.files['file']
    user_prompt = request.form.get('prompt', '')
    
    # 保存文件
    save_result = save_uploaded_file(file, 'audio')
    if not save_result['success']:
        return jsonify(save_result)
    
    # 处理音频（转录 + 回应）
    process_result = process_audio_message(save_result['path'], user_prompt)
    
    return jsonify({
        'success': process_result['success'],
        'filename': save_result['filename'],
        'path': save_result['path'],
        'transcription': process_result.get('transcription', ''),
        'response': process_result.get('response', ''),
        'error': process_result.get('error', '')
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取上传统计"""
    stats = get_upload_stats()
    return jsonify({
        'success': True,
        'stats': stats,
        'supported_images': SUPPORTED_IMAGE_FORMATS,
        'supported_audio': SUPPORTED_AUDIO_FORMATS
    })


@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """清理旧文件"""
    days = request.json.get('days', 7) if request.json else 7
    cleaned = cleanup_old_files(days)
    return jsonify({
        'success': True,
        'cleaned': cleaned
    })


# ==================== 辅助函数 ====================

def test_llm_connection(config):
    """测试 LLM 连接"""
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', 'https://api.openai.com/v1')
    model = config.get('model', 'gpt-3.5-turbo')
    
    url = f"{base_url}/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': 'Hello!'}],
        'max_tokens': 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return {
            'success': True,
            'message': '连接成功！',
            'model': model
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'连接失败：{str(e)}'
        }


# ==================== HTML 模板（黑色主题） ====================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pandaco.asia - AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
            background: #0a0a0a;
            color: #00ff00;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* 头部 */
        header {
            background: #111;
            border-bottom: 1px solid #00ff00;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #00ff00;
            text-decoration: none;
            letter-spacing: 2px;
        }
        
        .logo:hover {
            text-shadow: 0 0 10px #00ff00;
        }
        
        .header-status {
            font-size: 12px;
            color: #00aa00;
        }
        
        /* 导航 */
        .nav-tabs {
            display: flex;
            background: #111;
            border-bottom: 1px solid #333;
        }
        
        .nav-tab {
            flex: 1;
            padding: 15px;
            background: transparent;
            color: #00aa00;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.3s;
        }
        
        .nav-tab:hover {
            background: #1a1a1a;
            color: #00ff00;
        }
        
        .nav-tab.active {
            background: #1a1a1a;
            color: #00ff00;
            border-bottom-color: #00ff00;
        }
        
        /* 主容器 */
        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            padding: 20px;
        }
        
        .chat-container, .config-container, .multimodal-container {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .chat-container.hidden, .config-container.hidden, .multimodal-container.hidden {
            display: none;
        }
        
        /* 聊天消息区域 */
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #0f0f0f;
            border: 1px solid #333;
            border-radius: 8px;
            margin-bottom: 20px;
            min-height: 500px;
        }
        
        .message {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 8px;
            animation: fadeIn 0.3s ease;
            max-width: 80%;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            background: #1a3a1a;
            color: #00ff00;
            margin-left: auto;
            border: 1px solid #00aa00;
        }
        
        .message.assistant {
            background: #1a1a1a;
            color: #00ff00;
            margin-right: auto;
            border: 1px solid #333;
        }
        
        .message.error {
            background: #3a1a1a;
            color: #ff6666;
            border: 1px solid #ff0000;
        }
        
        .message-image {
            max-width: 100%;
            max-height: 300px;
            border-radius: 8px;
            margin-top: 10px;
            border: 1px solid #00aa00;
        }
        
        /* 输入区域 */
        .chat-input-area {
            background: #111;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
        }
        
        .image-preview-container {
            display: none;
            margin-bottom: 10px;
            padding: 10px;
            background: #1a1a1a;
            border-radius: 8px;
            border: 1px solid #00aa00;
        }
        
        .image-preview {
            max-width: 200px;
            max-height: 150px;
            border-radius: 4px;
            margin-right: 10px;
        }
        
        .remove-image {
            background: #3a1a1a;
            color: #ff6666;
            border: 1px solid #ff0000;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .chat-input-wrapper {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 15px;
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #00ff00;
            font-size: 14px;
            font-family: inherit;
            outline: none;
        }
        
        .chat-input:focus {
            border-color: #00ff00;
        }
        
        .chat-input::placeholder {
            color: #006600;
        }
        
        .upload-btn, .send-btn {
            padding: 12px 20px;
            background: #1a3a1a;
            color: #00ff00;
            border: 1px solid #00aa00;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }
        
        .upload-btn:hover, .send-btn:hover {
            background: #2a5a2a;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }
        
        .upload-btn:disabled, .send-btn:disabled {
            background: #333;
            border-color: #555;
            color: #666;
            cursor: not-allowed;
        }
        
        .file-input {
            display: none;
        }
        
        /* 配置表单 */
        .config-form {
            background: #0f0f0f;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #00ff00;
            font-size: 14px;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #00ff00;
            font-size: 14px;
            font-family: inherit;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #00ff00;
        }
        
        .form-group small {
            display: block;
            margin-top: 5px;
            color: #006600;
            font-size: 12px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
            margin-right: 10px;
        }
        
        .btn-primary {
            background: #1a3a1a;
            color: #00ff00;
            border: 1px solid #00aa00;
        }
        
        .btn-primary:hover {
            background: #2a5a2a;
        }
        
        .btn-success {
            background: #1a5a1a;
            color: #00ff00;
            border: 1px solid #00ff00;
        }
        
        .btn-success:hover {
            background: #2a7a2a;
        }
        
        .btn-danger {
            background: #5a1a1a;
            color: #ff6666;
            border: 1px solid #ff0000;
        }
        
        .btn-danger:hover {
            background: #7a2a2a;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .alert-success {
            background: #1a3a1a;
            color: #00ff00;
            border: 1px solid #00aa00;
        }
        
        .alert-error {
            background: #3a1a1a;
            color: #ff6666;
            border: 1px solid #ff0000;
        }
        
        .alert-info {
            background: #1a2a3a;
            color: #66aaff;
            border: 1px solid #4488cc;
        }
        
        /* 多模态标签 */
        .tab-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tab-btn {
            padding: 10px 20px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #00aa00;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }
        
        .tab-btn.active {
            background: #1a3a1a;
            color: #00ff00;
            border-color: #00aa00;
        }
        
        .tab-btn:hover:not(.active) {
            background: #2a2a2a;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* 上传区域 */
        .upload-area {
            border: 2px dashed #333;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: #00ff00;
            background: #1a1a1a;
        }
        
        .upload-area.dragover {
            border-color: #00ff00;
            background: #1a3a1a;
        }
        
        .upload-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        .preview-container {
            margin-top: 20px;
            padding: 15px;
            background: #1a1a1a;
            border-radius: 8px;
            border: 1px solid #333;
        }
        
        .preview-image {
            max-width: 100%;
            max-height: 400px;
            border-radius: 8px;
            border: 1px solid #00aa00;
        }
        
        .audio-player {
            width: 100%;
            margin-top: 10px;
        }
        
        .result-box {
            margin-top: 20px;
            padding: 15px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
        }
        
        .result-box h4 {
            margin-bottom: 10px;
            color: #00ff00;
        }
        
        .result-box pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #0a0a0a;
            padding: 10px;
            border-radius: 5px;
            color: #00cc00;
        }
        
        /* 统计卡片 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #333;
        }
        
        .stat-card h3 {
            font-size: 2em;
            color: #00ff00;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            color: #00aa00;
            font-size: 14px;
        }
        
        /* 加载动画 */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #333;
            border-top: 3px solid #00ff00;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* 滚动条 */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0a0a0a;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #00aa00;
        }
    </style>
</head>
<body>
    <header>
        <a href="#" class="logo">pandaco.asia</a>
        <div class="header-status">● Online</div>
    </header>
    
    <div class="nav-tabs">
        <button class="nav-tab active" onclick="switchTab('chat')">💬 Chat</button>
        <button class="nav-tab" onclick="switchTab('multimodal')">🖼️ Multimodal</button>
        <button class="nav-tab" onclick="switchTab('config')">⚙️ Settings</button>
    </div>
    
    <div class="container">
        <!-- 聊天界面 -->
        <div id="chat-tab" class="chat-container">
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant">
                    👋 Hello! I'm your AI assistant. How can I help you today?
                </div>
            </div>
            
            <div class="chat-input-area">
                <div class="image-preview-container" id="image-preview-container">
                    <img id="image-preview" class="image-preview" src="">
                    <button class="remove-image" onclick="removeImage()">✕ Remove</button>
                </div>
                
                <div class="chat-input-wrapper">
                    <input type="file" id="chat-image-input" class="file-input" accept="image/*" onchange="handleChatImage(this.files[0])">
                    <button class="upload-btn" onclick="document.getElementById('chat-image-input').click()" title="Upload Image">📷</button>
                    <input type="text" id="chat-input" class="chat-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter')sendMessage()">
                    <button id="send-btn" class="send-btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
        
        <!-- 多模态界面 -->
        <div id="multimodal-tab" class="multimodal-container hidden">
            <div class="config-form">
                <div class="tab-buttons">
                    <button class="tab-btn active" onclick="switchMultimodalTab('image')">🖼️ Image</button>
                    <button class="tab-btn" onclick="switchMultimodalTab('audio')">🎤 Audio</button>
                    <button class="tab-btn" onclick="switchMultimodalTab('stats')">📊 Stats</button>
                </div>
                
                <!-- 图片识别 -->
                <div id="image-tab" class="tab-content active">
                    <div class="alert alert-info">
                        💡 Upload an image for AI analysis. Supported: JPG, PNG, GIF, WebP
                    </div>
                    
                    <div class="upload-area" id="image-drop-zone" onclick="document.getElementById('image-input').click()">
                        <div class="upload-icon">🖼️</div>
                        <p>Click or drag to upload image</p>
                        <input type="file" id="image-input" class="file-input" accept="image/*" onchange="handleImageUpload(this.files[0])">
                    </div>
                    
                    <div class="form-group">
                        <label>Prompt</label>
                        <input type="text" id="image-prompt" value="Please describe this image in detail" placeholder="What do you want to know?">
                    </div>
                    
                    <div id="image-preview-box" class="preview-container" style="display:none;">
                        <h4>Preview</h4>
                        <img id="image-preview-img" class="preview-image" src="">
                    </div>
                    
                    <div id="image-result" class="result-box" style="display:none;">
                        <h4>Analysis Result</h4>
                        <pre id="image-result-text"></pre>
                    </div>
                </div>
                
                <!-- 音频识别 -->
                <div id="audio-tab" class="tab-content">
                    <div class="alert alert-info">
                        💡 Upload audio for transcription. Supported: MP3, WAV, OGG, M4A
                        <br><small>⚠️ Requires OpenAI API for speech recognition</small>
                    </div>
                    
                    <div class="upload-area" id="audio-drop-zone" onclick="document.getElementById('audio-input').click()">
                        <div class="upload-icon">🎤</div>
                        <p>Click or drag to upload audio</p>
                        <input type="file" id="audio-input" class="file-input" accept="audio/*" onchange="handleAudioUpload(this.files[0])">
                    </div>
                    
                    <div class="form-group">
                        <label>Additional Prompt (optional)</label>
                        <input type="text" id="audio-prompt" placeholder="How should AI respond?">
                    </div>
                    
                    <div id="audio-preview-box" class="preview-container" style="display:none;">
                        <h4>Preview</h4>
                        <audio id="audio-preview-player" class="audio-player" controls>
                            <source src="" type="audio/mpeg">
                        </audio>
                    </div>
                    
                    <div id="audio-result" class="result-box" style="display:none;">
                        <h4>Transcription</h4>
                        <pre id="audio-transcription"></pre>
                        <h4 style="margin-top:15px;">AI Response</h4>
                        <pre id="audio-response"></pre>
                    </div>
                </div>
                
                <!-- 统计 -->
                <div id="stats-tab" class="tab-content">
                    <div class="stats-grid" id="stats-grid">
                        <div class="stat-card">
                            <h3>-</h3>
                            <p>Images</p>
                        </div>
                        <div class="stat-card">
                            <h3>-</h3>
                            <p>Audios</p>
                        </div>
                        <div class="stat-card">
                            <h3>-</h3>
                            <p>Total Size</p>
                        </div>
                    </div>
                    
                    <button class="btn btn-danger" onclick="cleanupFiles()">🗑️ Cleanup files older than 7 days</button>
                </div>
            </div>
        </div>
        
        <!-- 配置界面 -->
        <div id="config-tab" class="config-container hidden">
            <div class="config-form">
                <div id="config-alert"></div>
                
                <div class="form-group">
                    <label>Provider</label>
                    <select id="config-provider" onchange="updateProviderDefaults()">
                        <option value="moonshot">Kimi (月之暗面)</option>
                        <option value="dashscope">Qwen (通义千问)</option>
                        <option value="deepseek">DeepSeek</option>
                        <option value="openai">OpenAI</option>
                        <option value="zhipu">Zhipu AI</option>
                        <option value="baichuan">Baichuan AI</option>
                        <option value="custom">Custom</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>API Key</label>
                    <input type="password" id="config-api-key" placeholder="sk-...">
                    <small>Your API key is stored locally only</small>
                </div>
                
                <div class="form-group">
                    <label>Base URL</label>
                    <input type="text" id="config-base-url" placeholder="https://api.example.com/v1">
                </div>
                
                <div class="form-group">
                    <label>Model</label>
                    <input type="text" id="config-model" placeholder="Model name">
                </div>
                
                <div class="form-group">
                    <label>Temperature (0-2)</label>
                    <input type="number" id="config-temperature" value="0.7" min="0" max="2" step="0.1">
                </div>
                
                <div class="form-group">
                    <label>Max Tokens</label>
                    <input type="number" id="config-max-tokens" value="4096">
                </div>
                
                <button class="btn btn-primary" onclick="testConfig()">🔍 Test Connection</button>
                <button class="btn btn-success" onclick="saveConfig()">💾 Save Configuration</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentImageBase64 = null;
        
        // 切换主标签
        function switchTab(tab) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.chat-container, .multimodal-container, .config-container').forEach(c => {
                c.classList.add('hidden');
            });
            
            // 安全获取 event.target
            var target;
            if (event && event.target) {
                target = event.target;
            } else {
                var buttons = document.querySelectorAll('.nav-tab');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].getAttribute('onclick').indexOf(tab) > -1) {
                        target = buttons[i];
                        break;
                    }
                }
            }
            if (target) target.classList.add('active');
            document.getElementById(tab + '-tab').classList.remove('hidden');
            
            if (tab === 'multimodal') {
                loadStats();
            }
        }
        
        // 切换多模态子标签
        function switchMultimodalTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // 安全获取 event.target
            var target;
            if (event && event.target) {
                target = event.target;
            } else {
                var buttons = document.querySelectorAll('.tab-btn');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].getAttribute('onclick').indexOf(tab) > -1) {
                        target = buttons[i];
                        break;
                    }
                }
            }
            if (target) target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }
        
        // 处理聊天中的图片
        function handleChatImage(file) {
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                currentImageBase64 = e.target.result;
                document.getElementById('image-preview').src = currentImageBase64;
                document.getElementById('image-preview-container').style.display = 'flex';
                document.getElementById('image-preview-container').style.alignItems = 'center';
            };
            reader.readAsDataURL(file);
        }
        
        // 移除图片
        function removeImage() {
            currentImageBase64 = null;
            document.getElementById('chat-image-input').value = '';
            document.getElementById('image-preview-container').style.display = 'none';
        }
        
        // 发送消息
        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            const sendBtn = document.getElementById('send-btn');
            
            if (!message && !currentImageBase64) return;
            
            const messagesDiv = document.getElementById('chat-messages');
            
            // 构建用户消息 HTML
            let userHtml = '';
            if (message) {
                userHtml += `<div>${escapeHtml(message)}</div>`;
            }
            if (currentImageBase64) {
                userHtml += `<img src="${currentImageBase64}" class="message-image">`;
            }
            
            // 添加用户消息
            messagesDiv.innerHTML += `<div class="message user">${userHtml}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            // 清空输入
            input.value = '';
            sendBtn.disabled = true;
            
            // 显示搜索状态
            const searchStatusId = 'search-status-' + Date.now();
            messagesDiv.innerHTML += `<div id="${searchStatusId}" class="message assistant" style="color:#00aa00;font-size:12px;">🔍 正在搜索实时信息...</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            // 发送请求
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: message,
                        image: currentImageBase64
                    })
                });
                
                const data = await response.json();
                
                // 移除搜索状态
                const searchStatusEl = document.getElementById(searchStatusId);
                if (searchStatusEl) {
                    searchStatusEl.remove();
                }
                
                if (data.success) {
                    // 如果有搜索，添加搜索指示器
                    let responseHtml = '';
                    if (data.has_search && data.search_status === 'completed') {
                        responseHtml += `<div style="font-size:11px;color:#00aa00;margin-bottom:8px;">✅ 已获取实时网络信息</div>`;
                    }
                    responseHtml += `<div>${formatResponse(data.response)}</div>`;
                    messagesDiv.innerHTML += `<div class="message assistant">${responseHtml}</div>`;
                } else {
                    messagesDiv.innerHTML += `<div class="message error">❌ ${escapeHtml(data.error || 'Request failed')}</div>`;
                }
            } catch (error) {
                const searchStatusEl = document.getElementById(searchStatusId);
                if (searchStatusEl) {
                    searchStatusEl.remove();
                }
                messagesDiv.innerHTML += `<div class="message error">❌ ${escapeHtml(error.message)}</div>`;
            }
            
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            sendBtn.disabled = false;
            removeImage();
        }
        
        // 格式化响应（支持 Markdown 简单渲染）
        function formatResponse(text) {
            if (!text) return '';
            // 转义 HTML
            var html = escapeHtml(text);
            // 加粗 **text**
            html = html.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
            // 斜体 *text*
            html = html.replace(/\\*(.+?)\\*/g, '<em>$1</em>');
            // 链接 [text](url)
            html = html.replace(/\\[(.+?)\\]\\((.+?)\\)/g, '<a href="$2" target="_blank" style="color:#00ff00;text-decoration:underline;">$1</a>');
            // 换行
            html = html.replace(/\\n/g, '<br>');
            return html;
        }
        
        // 处理图片上传（多模态标签）
        async function handleImageUpload(file) {
            if (!file) return;
            
            const preview = document.getElementById('image-preview-box');
            const previewImg = document.getElementById('image-preview-img');
            const resultBox = document.getElementById('image-result');
            const resultText = document.getElementById('image-result-text');
            
            // 显示预览
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
            
            // 上传
            const formData = new FormData();
            formData.append('file', file);
            formData.append('prompt', document.getElementById('image-prompt').value);
            
            resultBox.style.display = 'block';
            resultText.innerHTML = '<span class="loading"></span> Analyzing...';
            
            try {
                const response = await fetch('/api/upload/image', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultText.textContent = data.result;
                } else {
                    resultText.textContent = '❌ ' + (data.error || 'Analysis failed');
                }
            } catch (error) {
                resultText.textContent = '❌ ' + error.message;
            }
        }
        
        // 处理音频上传
        async function handleAudioUpload(file) {
            if (!file) return;
            
            const preview = document.getElementById('audio-preview-box');
            const previewPlayer = document.getElementById('audio-preview-player');
            const resultBox = document.getElementById('audio-result');
            const transcription = document.getElementById('audio-transcription');
            const response = document.getElementById('audio-response');
            
            // 显示预览
            const url = URL.createObjectURL(file);
            previewPlayer.src = url;
            preview.style.display = 'block';
            
            // 上传
            const formData = new FormData();
            formData.append('file', file);
            formData.append('prompt', document.getElementById('audio-prompt').value);
            
            resultBox.style.display = 'block';
            transcription.innerHTML = '<span class="loading"></span> Transcribing...';
            response.innerHTML = '';
            
            try {
                const response = await fetch('/api/upload/audio', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    transcription.textContent = data.transcription || 'None';
                    response.textContent = data.response || 'None';
                } else {
                    transcription.textContent = '❌ ' + (data.error || 'Processing failed');
                    response.textContent = '';
                }
            } catch (error) {
                transcription.textContent = '❌ ' + error.message;
                response.textContent = '';
            }
        }
        
        // 加载统计
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (data.success) {
                    const stats = data.stats;
                    document.getElementById('stats-grid').innerHTML = `
                        <div class="stat-card">
                            <h3>${stats.images}</h3>
                            <p>Images</p>
                        </div>
                        <div class="stat-card">
                            <h3>${stats.audio}</h3>
                            <p>Audios</p>
                        </div>
                        <div class="stat-card">
                            <h3>${(stats.total_size / 1024 / 1024).toFixed(2)} MB</h3>
                            <p>Total Size</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        // 清理文件
        async function cleanupFiles() {
            if (!confirm('Are you sure you want to delete files older than 7 days?')) return;
            
            try {
                const response = await fetch('/api/cleanup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({days: 7})
                });
                
                const data = await response.json();
                if (data.success) {
                    alert(`Cleaned ${data.cleaned} files`);
                    loadStats();
                }
            } catch (error) {
                alert('Cleanup failed: ' + error.message);
            }
        }
        
        // 更新提供商默认值
        function updateProviderDefaults() {
            const provider = document.getElementById('config-provider').value;
            const baseUrl = document.getElementById('config-base-url');
            const model = document.getElementById('config-model');
            
            const defaults = {
                moonshot: {url: 'https://api.moonshot.cn/v1', model: 'kimi-latest'},
                dashscope: {url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-max'},
                deepseek: {url: 'https://api.deepseek.com/v1', model: 'deepseek-chat'},
                openai: {url: 'https://api.openai.com/v1', model: 'gpt-4o'},
                zhipu: {url: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4'},
                baichuan: {url: 'https://api.baichuan-ai.com/v1', model: 'Baichuan4'}
            };
            
            if (defaults[provider]) {
                baseUrl.value = defaults[provider].url;
                model.value = defaults[provider].model;
            }
        }
        
        // 测试配置
        async function testConfig() {
            const config = getConfig();
            if (!config) return;
            
            const alertDiv = document.getElementById('config-alert');
            alertDiv.innerHTML = '<div class="alert alert-info">🔍 Testing connection...</div>';
            
            try {
                const response = await fetch('/api/config/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(config)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alertDiv.innerHTML = `<div class="alert alert-success">✅ ${data.message} (Model: ${data.model})</div>`;
                } else {
                    alertDiv.innerHTML = `<div class="alert alert-error">❌ ${data.message}</div>`;
                }
            } catch (error) {
                alertDiv.innerHTML = `<div class="alert alert-error">❌ ${error.message}</div>`;
            }
        }
        
        // 保存配置
        async function saveConfig() {
            const config = getConfig();
            if (!config) return;
            
            const alertDiv = document.getElementById('config-alert');
            alertDiv.innerHTML = '<div class="alert alert-info">💾 Saving...</div>';
            
            try {
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(config)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alertDiv.innerHTML = `<div class="alert alert-success">✅ ${data.message}</div>`;
                } else {
                    alertDiv.innerHTML = `<div class="alert alert-error">❌ ${data.error}</div>`;
                }
            } catch (error) {
                alertDiv.innerHTML = `<div class="alert alert-error">❌ ${error.message}</div>`;
            }
        }
        
        // 获取配置
        function getConfig() {
            const apiKey = document.getElementById('config-api-key').value.trim();
            if (!apiKey) {
                alert('API Key is required');
                return null;
            }
            
            return {
                provider: document.getElementById('config-provider').value,
                api_key: apiKey,
                base_url: document.getElementById('config-base-url').value.trim(),
                model: document.getElementById('config-model').value.trim(),
                temperature: parseFloat(document.getElementById('config-temperature').value),
                max_tokens: parseInt(document.getElementById('config-max-tokens').value)
            };
        }
        
        // HTML 转义
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // 拖拽上传（安全处理）
        window.addEventListener('DOMContentLoaded', function() {
            ['image-drop-zone', 'audio-drop-zone'].forEach(id => {
                const dropZone = document.getElementById(id);
                if (!dropZone) return;
                
                dropZone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    dropZone.classList.add('dragover');
                });
                
                dropZone.addEventListener('dragleave', () => {
                    dropZone.classList.remove('dragover');
                });
                
                dropZone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    dropZone.classList.remove('dragover');
                    
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        if (id === 'image-drop-zone') {
                            handleImageUpload(files[0]);
                        } else {
                            handleAudioUpload(files[0]);
                        }
                    }
                });
            });
        });
        
        // 页面加载时获取配置
        window.onload = async function() {
            try {
                const response = await fetch('/api/config');
                const data = await response.json();
                
                if (data.success && data.config) {
                    const cfg = data.config;
                    // 填充所有配置字段
                    if (cfg.provider) {
                        document.getElementById('config-provider').value = cfg.provider;
                        updateProviderDefaults();
                    }
                    document.getElementById('config-api-key').value = cfg.api_key || '';
                    document.getElementById('config-base-url').value = cfg.base_url || '';
                    document.getElementById('config-model').value = cfg.model || '';
                    document.getElementById('config-temperature').value = cfg.temperature || 0.7;
                    document.getElementById('config-max-tokens').value = cfg.max_tokens || 4096;
                    
                    console.log('✅ 配置已加载');
                }
            } catch (error) {
                console.error('Failed to load config:', error);
            }
        };
    </script>
</body>
</html>
"""


# ==================== 主路由 ====================

@app.route('/')
def index():
    """主页面"""
    return render_template_string(HTML_TEMPLATE)


# ==================== 主程序 ====================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenTalon Web Server')
    parser.add_argument('--port', type=int, default=6767, help='监听端口')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='监听地址')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    print(f"""
╔═══════════════════════════════════════╗
║     OpenTalon Web Server              ║
║     Black Theme Edition               ║
╚═══════════════════════════════════════╝

🌐 Access:
   Local: http://localhost:{args.port}
   LAN: http://{args.host}:{args.port}

📁 Upload Dir: {Path.home() / '.opentalon' / 'uploads'}

🚀 Starting server...
""")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
