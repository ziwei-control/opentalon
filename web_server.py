#!/usr/bin/env python3
"""
OpenTalon Web 界面 (增强版)
支持网页配置 API Key + 公网访问
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

# HTML 模板 (增强版 - 支持配置)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 OpenTalon - Web 界面</title>
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
            max-width: 900px;
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
        
        .chat-container, .config-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .config-container {
            display: none;
        }
        
        .config-container.active {
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
            border: 1px solid #fcc;
        }
        
        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .chat-input input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
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
            border-radius: 25px;
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
        
        .status-bar {
            padding: 10px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            font-size: 14px;
            color: #666;
        }
        
        .status-bar .status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .status-bar .status.online {
            background: #4caf50;
        }
        
        .status-bar .status.offline {
            background: #f44336;
        }
        
        .typing-indicator {
            display: none;
            padding: 15px;
            color: #666;
        }
        
        .typing-indicator.show {
            display: block;
        }
        
        .typing-indicator span {
            animation: blink 1.4s infinite both;
        }
        
        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes blink {
            0% { opacity: 0.2; }
            20% { opacity: 1; }
            100% { opacity: 0.2; }
        }
        
        .markdown-content {
            line-height: 1.6;
        }
        
        .markdown-content pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
        }
        
        .markdown-content code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
        }
        
        /* 配置表单样式 */
        .config-form {
            padding: 30px;
        }
        
        .config-form h2 {
            margin-bottom: 20px;
            color: #333;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus, .form-group select:focus {
            border-color: #667eea;
        }
        
        .form-group small {
            display: block;
            margin-top: 5px;
            color: #888;
            font-size: 13px;
        }
        
        .btn-save {
            padding: 15px 30px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn-save:hover {
            background: #45a049;
        }
        
        .btn-test {
            padding: 15px 30px;
            background: #2196f3;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
            margin-left: 10px;
        }
        
        .btn-test:hover {
            background: #1976d2;
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
        
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 OpenTalon</h1>
            <p>Markdown 驱动的本地化自主智能体</p>
        </header>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('chat')">💬 聊天</button>
            <button class="nav-tab" onclick="showTab('config')">⚙️ 配置</button>
        </div>
        
        <!-- 聊天界面 -->
        <div id="chatTab" class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <div class="markdown-content">
                        你好！我是 Talon，你的智能助手。有什么可以帮你的吗？
                    </div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                Talon 正在思考<span>.</span><span>.</span><span>.</span>
            </div>
            
            <div class="chat-input">
                <input 
                    type="text" 
                    id="userInput" 
                    placeholder="输入你的问题..." 
                    autocomplete="off"
                    autofocus
                >
                <button id="sendBtn" onclick="sendMessage()">发送</button>
            </div>
            
            <div class="status-bar">
                <span class="status" id="statusIndicator"></span>
                <span id="statusText">检查配置中...</span>
            </div>
        </div>
        
        <!-- 配置界面 -->
        <div id="configTab" class="config-container">
            <div class="config-form">
                <h2>⚙️ LLM 配置</h2>
                
                <div id="configAlert" class="alert hidden"></div>
                
                <div class="form-group">
                    <label for="provider">云模型提供商</label>
                    <select id="provider" onchange="updateProviderInfo()">
                        <option value="openai">OpenAI (GPT)</option>
                        <option value="moonshot">Kimi (月之暗面)</option>
                        <option value="dashscope">Qwen (通义千问)</option>
                        <option value="deepseek">DeepSeek (深度求索)</option>
                        <option value="zhipu">Zhipu (智谱 AI)</option>
                        <option value="baichuan">Baichuan (百川智能)</option>
                    </select>
                    <small>选择你的云模型提供商</small>
                </div>
                
                <div class="form-group">
                    <label for="apiKey">API Key</label>
                    <input type="password" id="apiKey" placeholder="sk-xxxxxxxxxxxxxxxx">
                    <small>你的 API Key，仅保存在本地</small>
                </div>
                
                <div class="form-group">
                    <label for="baseUrl">API Base URL</label>
                    <input type="text" id="baseUrl" placeholder="https://api.openai.com/v1">
                    <small>API 端点地址</small>
                </div>
                
                <div class="form-group">
                    <label for="model">模型名称</label>
                    <input type="text" id="model" placeholder="gpt-3.5-turbo">
                    <small>例如：gpt-4, kimi-latest, qwen-max</small>
                </div>
                
                <div class="form-group">
                    <label for="temperature">Temperature</label>
                    <input type="number" id="temperature" value="0.7" min="0" max="2" step="0.1">
                    <small>创造性程度 (0-2，默认 0.7)</small>
                </div>
                
                <button class="btn-save" onclick="saveConfig()">💾 保存配置</button>
                <button class="btn-test" onclick="testConnection()">🧪 测试连接</button>
            </div>
        </div>
    </div>
    
    <script>
        let messageHistory = [];
        let currentConfig = null;
        
        // 提供商预设
        const providerPresets = {
            'openai': {
                baseUrl: 'https://api.openai.com/v1',
                model: 'gpt-3.5-turbo'
            },
            'moonshot': {
                baseUrl: 'https://api.moonshot.cn/v1',
                model: 'kimi-latest'
            },
            'dashscope': {
                baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                model: 'qwen-max'
            },
            'deepseek': {
                baseUrl: 'https://api.deepseek.com/v1',
                model: 'deepseek-chat'
            },
            'zhipu': {
                baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
                model: 'glm-4'
            },
            'baichuan': {
                baseUrl: 'https://api.baichuan-ai.com/v1',
                model: 'Baichuan4'
            }
        };
        
        // 切换标签页
        function showTab(tabName) {
            const chatTab = document.getElementById('chatTab');
            const configTab = document.getElementById('configTab');
            const tabs = document.querySelectorAll('.nav-tab');
            
            if (tabName === 'chat') {
                chatTab.classList.remove('hidden');
                configTab.classList.remove('active');
                tabs[0].classList.add('active');
                tabs[1].classList.remove('active');
            } else {
                chatTab.classList.add('hidden');
                configTab.classList.add('active');
                tabs[0].classList.remove('active');
                tabs[1].classList.add('active');
                loadCurrentConfig();
            }
        }
        
        // 更新提供商信息
        function updateProviderInfo() {
            const provider = document.getElementById('provider').value;
            const preset = providerPresets[provider];
            if (preset) {
                document.getElementById('baseUrl').value = preset.baseUrl;
                document.getElementById('model').value = preset.model;
            }
        }
        
        // 检查 LLM 配置
        async function checkConfig() {
            try {
                const response = await fetch('/api/config');
                const data = await response.json();
                
                const statusIndicator = document.getElementById('statusIndicator');
                const statusText = document.getElementById('statusText');
                currentConfig = data;
                
                if (data.configured) {
                    statusIndicator.className = 'status online';
                    statusText.textContent = `已配置：${data.provider} (${data.model})`;
                } else {
                    statusIndicator.className = 'status offline';
                    statusText.textContent = '未配置 LLM，请在配置页设置 API Key';
                }
            } catch (error) {
                console.error('检查配置失败:', error);
            }
        }
        
        // 加载当前配置
        async function loadCurrentConfig() {
            try {
                const response = await fetch('/api/config');
                const data = await response.json();
                
                if (data.configured) {
                    // 映射 provider
                    const providerMap = {
                        'https://api.moonshot.cn/v1': 'moonshot',
                        'https://dashscope.aliyuncs.com/compatible-mode/v1': 'dashscope',
                        'https://api.deepseek.com/v1': 'deepseek',
                        'https://open.bigmodel.cn/api/paas/v4': 'zhipu',
                        'https://api.baichuan-ai.com/v1': 'baichuan'
                    };
                    
                    const provider = providerMap[data.base_url] || 'openai';
                    document.getElementById('provider').value = provider;
                    document.getElementById('apiKey').value = data.api_key || '';
                    document.getElementById('baseUrl').value = data.base_url;
                    document.getElementById('model').value = data.model;
                    document.getElementById('temperature').value = data.temperature || 0.7;
                    
                    updateProviderInfo();
                }
            } catch (error) {
                console.error('加载配置失败:', error);
            }
        }
        
        // 保存配置
        async function saveConfig() {
            const config = {
                provider: document.getElementById('provider').value,
                api_key: document.getElementById('apiKey').value,
                base_url: document.getElementById('baseUrl').value,
                model: document.getElementById('model').value,
                temperature: parseFloat(document.getElementById('temperature').value),
                max_tokens: 4096,
                timeout: 60
            };
            
            if (!config.api_key) {
                showAlert('请输入 API Key', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(config)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert('✅ 配置保存成功！', 'success');
                    checkConfig();
                    setTimeout(() => showTab('chat'), 1000);
                } else {
                    showAlert('❌ 保存失败：' + data.error, 'error');
                }
            } catch (error) {
                showAlert('❌ 保存失败：' + error.message, 'error');
            }
        }
        
        // 测试连接
        async function testConnection() {
            const config = {
                provider: document.getElementById('provider').value,
                api_key: document.getElementById('apiKey').value,
                base_url: document.getElementById('baseUrl').value,
                model: document.getElementById('model').value
            };
            
            if (!config.api_key) {
                showAlert('请输入 API Key', 'error');
                return;
            }
            
            showAlert('🧪 正在测试连接...', 'info');
            
            try {
                const response = await fetch('/api/test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(config)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert('✅ 连接成功！' + (data.message || ''), 'success');
                } else {
                    showAlert('❌ 连接失败：' + data.error, 'error');
                }
            } catch (error) {
                showAlert('❌ 测试失败：' + error.message, 'error');
            }
        }
        
        // 显示提示
        function showAlert(message, type) {
            const alert = document.getElementById('configAlert');
            alert.textContent = message;
            alert.className = `alert alert-${type}`;
            alert.classList.remove('hidden');
            
            if (type !== 'info') {
                setTimeout(() => {
                    alert.classList.add('hidden');
                }, 5000);
            }
        }
        
        // 发送消息
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            const chatMessages = document.getElementById('chatMessages');
            const typingIndicator = document.getElementById('typingIndicator');
            
            const message = input.value.trim();
            if (!message) return;
            
            // 添加用户消息
            addMessage(message, 'user');
            input.value = '';
            input.disabled = true;
            sendBtn.disabled = true;
            
            // 显示打字指示
            typingIndicator.classList.add('show');
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        history: messageHistory
                    })
                });
                
                const data = await response.json();
                
                // 隐藏打字指示
                typingIndicator.classList.remove('show');
                
                if (data.error) {
                    addMessage(data.error, 'error');
                } else {
                    addMessage(data.response, 'assistant');
                    messageHistory.push({ role: 'user', content: message });
                    messageHistory.push({ role: 'assistant', content: data.response });
                }
            } catch (error) {
                typingIndicator.classList.remove('show');
                addMessage('❌ 请求失败：' + error.message, 'error');
            }
            
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
        
        // 添加消息到聊天界面
        function addMessage(content, type) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            // 简单的 Markdown 渲染
            let formatted = content
                .replace(/```([\\s\\S]*?)```/g, '<pre><code>$1</code></pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\*(.+?)\\*/g, '<em>$1</em>')
                .replace(/\\n/g, '<br>');
            
            messageDiv.innerHTML = `<div class="markdown-content">${formatted}</div>`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // 回车发送
        document.getElementById('userInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // 页面加载时检查配置
        checkConfig();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/config', methods=['GET'])
def get_config():
    config = load_llm_config()
    if config:
        return jsonify({
            'configured': True,
            'provider': config.get('provider', 'unknown'),
            'model': config.get('model', 'unknown'),
            'base_url': config.get('base_url', 'unknown'),
            'api_key': config.get('api_key', '')[:8] + '...' + config.get('api_key', '')[-4:] if config.get('api_key') else '',
            'temperature': config.get('temperature', 0.7)
        })
    else:
        return jsonify({'configured': False})

@app.route('/api/config', methods=['POST'])
def set_config():
    try:
        data = request.json
        config = {
            '_comment': 'OpenTalon LLM 配置 - 通过网页设置',
            '_docs': '详见 /home/admin/projects/opentalon/COMPLETE_GUIDE.md',
            'provider': data.get('provider', 'openai'),
            'api_key': data.get('api_key', ''),
            'base_url': data.get('base_url', 'https://api.openai.com/v1'),
            'model': data.get('model', 'gpt-3.5-turbo'),
            'temperature': data.get('temperature', 0.7),
            'max_tokens': data.get('max_tokens', 4096),
            'timeout': data.get('timeout', 60)
        }
        
        save_llm_config(config)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test', methods=['POST'])
def test_connection():
    try:
        data = request.json
        import requests
        
        api_key = data.get('api_key', '')
        base_url = data.get('base_url', 'https://api.openai.com/v1')
        model = data.get('model', 'gpt-3.5-turbo')
        
        url = f"{base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': 'Hello'}],
            'max_tokens': 10
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        return jsonify({
            'success': True,
            'message': 'API 连接正常'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    history = data.get('history', [])
    
    if not message:
        return jsonify({'error': '消息不能为空'})
    
    # 构建消息列表
    messages = [
        {
            'role': 'system',
            'content': '你是 Talon，一个 Markdown 驱动的本地化智能助手。说话直接、简洁、有帮助。'
        }
    ]
    messages.extend(history)
    messages.append({'role': 'user', 'content': message})
    
    # 调用 LLM
    response = call_llm(messages)
    
    return jsonify({'response': response})

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenTalon Web 服务器')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认：0.0.0.0)')
    parser.add_argument('--port', type=int, default=6767, help='端口 (默认：6767)')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    print("""
    ╔═══════════════════════════════════════╗
    ║     OpenTalon Web 界面 (增强版)        ║
    ║        支持网页配置 API Key            ║
    ╚═══════════════════════════════════════╝
    """)
    
    print(f"🌐 启动 Web 服务器...")
    print(f"   地址：http://{args.host}:{args.port}")
    print(f"   公网：http://你的IP:{args.port}")
    print(f"   调试：{'是' if args.debug else '否'}")
    print("")
    print("💡 提示:")
    print("  - 访问 http://localhost:6767 使用 Web 界面")
    print("  - 配置页可以设置 API Key")
    print("  - 按 Ctrl+C 停止服务器")
    print("")
    
    # 检查 Flask 依赖
    try:
        import flask
        import flask_cors
    except ImportError:
        print("❌ 缺少依赖：需要安装 Flask")
        print("")
        print("运行以下命令安装:")
        print("  pip3 install flask flask-cors")
        print("")
        sys.exit(1)
    
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
