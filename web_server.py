#!/usr/bin/env python3
"""
OpenTalon Web 界面 (多模态增强版)
支持：
- 网页配置 API Key
- 图片上传与识别
- 音频上传与语音识别
- 公网访问
"""

import os
import sys
import json
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
    import requests
    
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
        # 隐藏敏感信息
        if 'api_key' in config:
            config['api_key'] = config['api_key'][:8] + '...' if len(config['api_key']) > 8 else '***'
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
    
    # 保存配置
    save_llm_config(data)
    
    # 测试连接
    test_result = test_llm_connection(data)
    
    return jsonify({
        'success': True,
        'message': '配置已保存',
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
    """文字聊天"""
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': '消息不能为空'})
    
    message = data['message']
    response = call_llm([{'role': 'user', 'content': message}])
    
    return jsonify({
        'success': True,
        'response': response
    })


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
    import requests
    
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


# ==================== HTML 模板 ====================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 OpenTalon - 多模态 Web 界面</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .nav-tabs {
            display: flex;
            margin-bottom: 20px;
        }
        
        .nav-tab {
            flex: 1;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        
        .nav-tab:first-child {
            border-radius: 10px 0 0 10px;
        }
        
        .nav-tab:last-child {
            border-radius: 0 10px 10px 0;
        }
        
        .nav-tab.active {
            background: white;
            color: #667eea;
            font-weight: bold;
        }
        
        .nav-tab:hover:not(.active) {
            background: rgba(255,255,255,0.3);
        }
        
        .chat-container, .config-container, .multimodal-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .config-container, .multimodal-container {
            display: none;
        }
        
        .config-container.active, .multimodal-container.active {
            display: block;
        }
        
        .chat-container.hidden {
            display: none;
        }
        
        .chat-messages {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 10px;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            background: #667eea;
            color: white;
            margin-left: 20%;
        }
        
        .message.assistant {
            background: white;
            color: #333;
            margin-right: 20%;
            border: 1px solid #e0e0e0;
        }
        
        .message.error {
            background: #fee;
            color: #c00;
            margin-right: 20%;
        }
        
        .chat-input {
            display: flex;
            padding: 20px;
            border-top: 1px solid #e0e0e0;
        }
        
        .chat-input input {
            flex: 1;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            outline: none;
        }
        
        .chat-input input:focus {
            border-color: #667eea;
        }
        
        .chat-input button {
            margin-left: 10px;
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .chat-input button:hover {
            background: #5568d3;
        }
        
        .chat-input button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .config-form {
            padding: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-group small {
            display: block;
            margin-top: 5px;
            color: #666;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        /* 多模态样式 */
        .upload-area {
            border: 2px dashed #ddd;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            transition: all 0.3s;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background: #f8f9fa;
        }
        
        .upload-area.dragover {
            border-color: #667eea;
            background: #eef;
        }
        
        .upload-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        .file-input {
            display: none;
        }
        
        .file-label {
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .file-label:hover {
            background: #5568d3;
        }
        
        .preview-container {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .preview-image {
            max-width: 100%;
            max-height: 400px;
            border-radius: 8px;
        }
        
        .audio-player {
            width: 100%;
            margin-top: 10px;
        }
        
        .result-box {
            margin-top: 20px;
            padding: 15px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        
        .result-box h4 {
            margin-bottom: 10px;
            color: #667eea;
        }
        
        .result-box pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
        }
        
        .tab-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tab-btn {
            padding: 10px 20px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tab-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .tab-btn:hover:not(.active) {
            background: #e9ecef;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2em;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 OpenTalon</h1>
            <p>Markdown 驱动的本地化自主智能体 - 多模态版</p>
        </header>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="switchTab('chat')">💬 聊天</button>
            <button class="nav-tab" onclick="switchTab('multimodal')">🖼️ 多模态</button>
            <button class="nav-tab" onclick="switchTab('config')">⚙️ 配置</button>
        </div>
        
        <!-- 聊天界面 -->
        <div id="chat-tab" class="chat-container">
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant">
                    👋 你好！我是 OpenTalon，你的 AI 助手。有什么可以帮你的吗？
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="chat-input" placeholder="输入消息..." onkeypress="if(event.key==='Enter')sendMessage()">
                <button id="send-btn" onclick="sendMessage()">发送</button>
            </div>
        </div>
        
        <!-- 多模态界面 -->
        <div id="multimodal-tab" class="multimodal-container">
            <div class="config-form">
                <div class="tab-buttons">
                    <button class="tab-btn active" onclick="switchMultimodalTab('image')">🖼️ 图片识别</button>
                    <button class="tab-btn" onclick="switchMultimodalTab('audio')">🎤 音频识别</button>
                    <button class="tab-btn" onclick="switchMultimodalTab('stats')">📊 统计</button>
                </div>
                
                <!-- 图片识别 -->
                <div id="image-tab" class="tab-content active">
                    <div class="alert alert-info">
                        💡 上传图片，让 AI 帮你识别和分析。支持格式：JPG, PNG, GIF, WebP
                    </div>
                    
                    <div class="upload-area" id="image-drop-zone" onclick="document.getElementById('image-input').click()">
                        <div class="upload-icon">🖼️</div>
                        <p>点击或拖拽上传图片</p>
                        <input type="file" id="image-input" class="file-input" accept="image/*" onchange="handleImageUpload(this.files[0])">
                    </div>
                    
                    <div class="form-group">
                        <label>识别提示词</label>
                        <input type="text" id="image-prompt" value="请详细描述这张图片" placeholder="你想让 AI 分析什么？">
                    </div>
                    
                    <div id="image-preview" class="preview-container" style="display:none;">
                        <h4>预览</h4>
                        <img id="image-preview-img" class="preview-image" src="">
                    </div>
                    
                    <div id="image-result" class="result-box" style="display:none;">
                        <h4>识别结果</h4>
                        <pre id="image-result-text"></pre>
                    </div>
                </div>
                
                <!-- 音频识别 -->
                <div id="audio-tab" class="tab-content">
                    <div class="alert alert-info">
                        💡 上传音频，AI 会转录文字并回应。支持格式：MP3, WAV, OGG, M4A
                        <br><small>⚠️ 注意：语音识别需要 OpenAI API</small>
                    </div>
                    
                    <div class="upload-area" id="audio-drop-zone" onclick="document.getElementById('audio-input').click()">
                        <div class="upload-icon">🎤</div>
                        <p>点击或拖拽上传音频</p>
                        <input type="file" id="audio-input" class="file-input" accept="audio/*" onchange="handleAudioUpload(this.files[0])">
                    </div>
                    
                    <div class="form-group">
                        <label>额外提示（可选）</label>
                        <input type="text" id="audio-prompt" placeholder="你想让 AI 如何回应？">
                    </div>
                    
                    <div id="audio-preview" class="preview-container" style="display:none;">
                        <h4>预览</h4>
                        <audio id="audio-preview-player" class="audio-player" controls>
                            <source src="" type="audio/mpeg">
                        </audio>
                    </div>
                    
                    <div id="audio-result" class="result-box" style="display:none;">
                        <h4>转录文字</h4>
                        <pre id="audio-transcription"></pre>
                        <h4 style="margin-top:15px;">AI 回应</h4>
                        <pre id="audio-response"></pre>
                    </div>
                </div>
                
                <!-- 统计 -->
                <div id="stats-tab" class="tab-content">
                    <div class="stats-grid" id="stats-grid">
                        <div class="stat-card">
                            <h3>-</h3>
                            <p>上传图片</p>
                        </div>
                        <div class="stat-card">
                            <h3>-</h3>
                            <p>上传音频</p>
                        </div>
                        <div class="stat-card">
                            <h3>-</h3>
                            <p>总大小</p>
                        </div>
                    </div>
                    
                    <button class="btn btn-danger" onclick="cleanupFiles()">🗑️ 清理 7 天前的文件</button>
                </div>
            </div>
        </div>
        
        <!-- 配置界面 -->
        <div id="config-tab" class="config-container">
            <div class="config-form">
                <div id="config-alert"></div>
                
                <div class="form-group">
                    <label>提供商</label>
                    <select id="config-provider" onchange="updateProviderDefaults()">
                        <option value="moonshot">Kimi (月之暗面)</option>
                        <option value="dashscope">Qwen (通义千问)</option>
                        <option value="deepseek">DeepSeek</option>
                        <option value="openai">OpenAI</option>
                        <option value="zhipu">智谱 AI</option>
                        <option value="baichuan">百川 AI</option>
                        <option value="custom">自定义</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>API Key</label>
                    <input type="password" id="config-api-key" placeholder="sk-...">
                    <small>你的 API Key 只保存在本地</small>
                </div>
                
                <div class="form-group">
                    <label>Base URL</label>
                    <input type="text" id="config-base-url" placeholder="https://api.example.com/v1">
                </div>
                
                <div class="form-group">
                    <label>模型</label>
                    <input type="text" id="config-model" placeholder="模型名称">
                </div>
                
                <div class="form-group">
                    <label>Temperature (0-2)</label>
                    <input type="number" id="config-temperature" value="0.7" min="0" max="2" step="0.1">
                </div>
                
                <div class="form-group">
                    <label>Max Tokens</label>
                    <input type="number" id="config-max-tokens" value="4096">
                </div>
                
                <button class="btn btn-primary" onclick="testConfig()">🔍 测试连接</button>
                <button class="btn btn-success" onclick="saveConfig()">💾 保存配置</button>
            </div>
        </div>
    </div>
    
    <script>
        // 切换主标签
        function switchTab(tab) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.chat-container, .multimodal-container, .config-container').forEach(c => {
                c.classList.remove('active');
                c.classList.add('hidden');
            });
            
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
            document.getElementById(tab + '-tab').classList.remove('hidden');
            
            if (tab === 'multimodal') {
                loadStats();
            }
        }
        
        // 切换多模态子标签
        function switchMultimodalTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }
        
        // 发送消息
        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;
            
            const messagesDiv = document.getElementById('chat-messages');
            const sendBtn = document.getElementById('send-btn');
            
            // 添加用户消息
            messagesDiv.innerHTML += `<div class="message user">${escapeHtml(message)}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            input.value = '';
            sendBtn.disabled = true;
            
            // 发送请求
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    messagesDiv.innerHTML += `<div class="message assistant">${escapeHtml(data.response)}</div>`;
                } else {
                    messagesDiv.innerHTML += `<div class="message error">❌ ${escapeHtml(data.error || '请求失败')}</div>`;
                }
            } catch (error) {
                messagesDiv.innerHTML += `<div class="message error">❌ ${escapeHtml(error.message)}</div>`;
            }
            
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            sendBtn.disabled = false;
        }
        
        // 处理图片上传
        async function handleImageUpload(file) {
            if (!file) return;
            
            const preview = document.getElementById('image-preview');
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
            resultText.innerHTML = '<span class="loading"></span> 正在识别...';
            
            try {
                const response = await fetch('/api/upload/image', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultText.textContent = data.result;
                } else {
                    resultText.textContent = '❌ ' + (data.error || '识别失败');
                }
            } catch (error) {
                resultText.textContent = '❌ ' + error.message;
            }
        }
        
        // 处理音频上传
        async function handleAudioUpload(file) {
            if (!file) return;
            
            const preview = document.getElementById('audio-preview');
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
            transcription.innerHTML = '<span class="loading"></span> 正在转录...';
            response.innerHTML = '';
            
            try {
                const response = await fetch('/api/upload/audio', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    transcription.textContent = data.transcription || '无';
                    response.textContent = data.response || '无';
                } else {
                    transcription.textContent = '❌ ' + (data.error || '处理失败');
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
                            <p>上传图片</p>
                        </div>
                        <div class="stat-card">
                            <h3>${stats.audio}</h3>
                            <p>上传音频</p>
                        </div>
                        <div class="stat-card">
                            <h3>${(stats.total_size / 1024 / 1024).toFixed(2)} MB</h3>
                            <p>总大小</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('加载统计失败:', error);
            }
        }
        
        // 清理文件
        async function cleanupFiles() {
            if (!confirm('确定要清理 7 天前的文件吗？')) return;
            
            try {
                const response = await fetch('/api/cleanup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({days: 7})
                });
                
                const data = await response.json();
                if (data.success) {
                    alert(`已清理 ${data.cleaned} 个文件`);
                    loadStats();
                }
            } catch (error) {
                alert('清理失败：' + error.message);
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
            alertDiv.innerHTML = '<div class="alert alert-info">🔍 正在测试连接...</div>';
            
            try {
                const response = await fetch('/api/config/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(config)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alertDiv.innerHTML = `<div class="alert alert-success">✅ ${data.message} (模型：${data.model})</div>`;
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
            alertDiv.innerHTML = '<div class="alert alert-info">💾 正在保存...</div>';
            
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
                alert('API Key 不能为空');
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
        
        // 拖拽上传
        ['image-drop-zone', 'audio-drop-zone'].forEach(id => {
            const dropZone = document.getElementById(id);
            
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
        
        // 页面加载时获取配置
        window.onload = async function() {
            try {
                const response = await fetch('/api/config');
                const data = await response.json();
                
                if (data.success && data.config && data.config.provider) {
                    document.getElementById('config-provider').value = data.config.provider;
                    updateProviderDefaults();
                    document.getElementById('config-base-url').value = data.config.base_url || '';
                    document.getElementById('config-model').value = data.config.model || '';
                    document.getElementById('config-temperature').value = data.config.temperature || 0.7;
                    document.getElementById('config-max-tokens').value = data.config.max_tokens || 4096;
                }
            } catch (error) {
                console.error('加载配置失败:', error);
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
║     多模态增强版 (图片 + 音频)          ║
╚═══════════════════════════════════════╝

🌐 访问地址:
   本地：http://localhost:{args.port}
   局域网：http://{args.host}:{args.port}

📁 上传目录：{Path.home() / '.opentalon' / 'uploads'}

🚀 启动服务...
""")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
