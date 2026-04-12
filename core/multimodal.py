#!/usr/bin/env python3
"""
OpenTalon 多模态处理模块
支持：
- 图片识别 (视觉模型)
- 音频识别 (语音转文字 + 回应)
- 文件上传处理
"""

import os
import base64
import json
import requests
from pathlib import Path
from datetime import datetime

# 上传目录
UPLOAD_DIR = Path.home() / '.opentalon' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 支持的格式
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac']


def load_llm_config():
    """加载 LLM 配置"""
    config_file = Path.home() / '.opentalon' / 'llm_config.json'
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_uploaded_file(file, file_type='image'):
    """
    保存上传的文件
    
    Args:
        file: Flask FileStorage 对象
        file_type: 'image' 或 'audio'
    
    Returns:
        dict: {'success': bool, 'path': str, 'filename': str, 'error': str}
    """
    if not file or file.filename == '':
        return {'success': False, 'error': '未选择文件'}
    
    # 检查文件扩展名
    ext = Path(file.filename).suffix.lower()
    
    if file_type == 'image' and ext not in SUPPORTED_IMAGE_FORMATS:
        return {
            'success': False,
            'error': f'不支持的图片格式，支持：{", ".join(SUPPORTED_IMAGE_FORMATS)}'
        }
    
    if file_type == 'audio' and ext not in SUPPORTED_AUDIO_FORMATS:
        return {
            'success': False,
            'error': f'不支持的音频格式，支持：{", ".join(SUPPORTED_AUDIO_FORMATS)}'
        }
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / file_type / safe_filename
    
    # 创建目录
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    try:
        file.save(str(file_path))
        return {
            'success': True,
            'path': str(file_path),
            'filename': safe_filename,
            'size': os.path.getsize(file_path)
        }
    except Exception as e:
        return {'success': False, 'error': f'保存失败：{str(e)}'}


def encode_image_to_base64(image_path):
    """将图片编码为 base64"""
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return None


def analyze_image(image_path, prompt='请描述这张图片'):
    """
    使用视觉模型分析图片
    
    Args:
        image_path: 图片路径
        prompt: 分析提示词
    
    Returns:
        dict: {'success': bool, 'result': str, 'error': str}
    """
    config = load_llm_config()
    if not config:
        return {'success': False, 'error': 'LLM 未配置'}
    
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', 'https://api.openai.com/v1')
    model = config.get('model', 'gpt-4o')
    
    # 检查是否支持视觉
    vision_models = ['gpt-4o', 'gpt-4-turbo', 'gpt-4-vision', 'qwen-vl', 'claude-3']
    is_vision = any(vm in model.lower() for vm in vision_models)
    
    if not is_vision:
        # 尝试使用支持的视觉模型
        if 'moonshot' in base_url:
            model = 'moonshot-v1-128k'  # Kimi 支持图片
        elif 'dashscope' in base_url:
            model = 'qwen-vl-max'
        elif 'openai' in base_url:
            model = 'gpt-4o'
    
    # 编码图片
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        return {'success': False, 'error': '无法读取图片'}
    
    # 检测图片类型
    ext = Path(image_path).suffix.lower()
    mime_type = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }.get(ext, 'image/jpeg')
    
    # 构建消息
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
    
    # 调用 API
    url = f"{base_url}/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model,
        'messages': messages,
        'max_tokens': config.get('max_tokens', 4096)
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        result = data['choices'][0]['message']['content']
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': f'识别失败：{str(e)}'}


def transcribe_audio(audio_path):
    """
    使用 Whisper API 转录音频
    
    Args:
        audio_path: 音频路径
    
    Returns:
        dict: {'success': bool, 'text': str, 'error': str}
    """
    config = load_llm_config()
    if not config:
        return {'success': False, 'error': 'LLM 未配置'}
    
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', 'https://api.openai.com/v1')
    
    # OpenAI Whisper API
    if 'openai' in base_url.lower():
        url = 'https://api.openai.com/v1/audio/transcriptions'
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        try:
            with open(audio_path, 'rb') as f:
                files = {'file': (Path(audio_path).name, f)}
                data = {'model': 'whisper-1'}
                response = requests.post(url, headers=headers, files=files, data=data, timeout=300)
                response.raise_for_status()
                result = response.json()
                return {'success': True, 'text': result.get('text', '')}
        except Exception as e:
            return {'success': False, 'error': f'转录失败：{str(e)}'}
    
    # 其他提供商（返回错误）
    return {
        'success': False,
        'error': '当前提供商不支持语音识别，请使用 OpenAI API'
    }


def process_audio_message(audio_path, user_prompt=''):
    """
    处理音频消息：转录 + LLM 回应
    
    Args:
        audio_path: 音频路径
        user_prompt: 额外的文字提示
    
    Returns:
        dict: {'success': bool, 'transcription': str, 'response': str, 'error': str}
    """
    # 第一步：转录音频
    transcription_result = transcribe_audio(audio_path)
    
    if not transcription_result['success']:
        return transcription_result
    
    transcription = transcription_result['text']
    
    # 第二步：使用 LLM 回应
    config = load_llm_config()
    if not config:
        return {'success': False, 'error': 'LLM 未配置'}
    
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', 'https://api.openai.com/v1')
    model = config.get('model', 'gpt-3.5-turbo')
    
    # 构建消息
    messages = [{
        'role': 'user',
        'content': f'以下是用户的语音消息："{transcription}"\n\n{user_prompt}' if user_prompt else f'以下是用户的语音消息："{transcription}"'
    }]
    
    # 调用 LLM
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
        llm_response = data['choices'][0]['message']['content']
        
        return {
            'success': True,
            'transcription': transcription,
            'response': llm_response
        }
    except Exception as e:
        return {
            'success': True,
            'transcription': transcription,
            'response': f'转录成功，但回应失败：{str(e)}'
        }


def get_upload_stats():
    """获取上传统计"""
    stats = {
        'images': 0,
        'audio': 0,
        'total_size': 0
    }
    
    # 统计图片
    image_dir = UPLOAD_DIR / 'image'
    if image_dir.exists():
        images = list(image_dir.glob('*'))
        stats['images'] = len(images)
        stats['total_size'] += sum(f.stat().st_size for f in images)
    
    # 统计音频
    audio_dir = UPLOAD_DIR / 'audio'
    if audio_dir.exists():
        audios = list(audio_dir.glob('*'))
        stats['audio'] = len(audios)
        stats['total_size'] += sum(f.stat().st_size for f in audios)
    
    return stats


def cleanup_old_files(days=7):
    """清理旧文件"""
    import time
    
    now = time.time()
    cutoff = now - (days * 86400)
    cleaned = 0
    
    for file_type in ['image', 'audio']:
        dir_path = UPLOAD_DIR / file_type
        if not dir_path.exists():
            continue
        
        for file_path in dir_path.glob('*'):
            if file_path.stat().st_mtime < cutoff:
                try:
                    file_path.unlink()
                    cleaned += 1
                except:
                    pass
    
    return cleaned


# 测试函数
if __name__ == '__main__':
    print("OpenTalon 多模态模块")
    print(f"上传目录：{UPLOAD_DIR}")
    print(f"支持的图片格式：{SUPPORTED_IMAGE_FORMATS}")
    print(f"支持的音频格式：{SUPPORTED_AUDIO_FORMATS}")
    
    stats = get_upload_stats()
    print(f"\n上传统计:")
    print(f"  图片：{stats['images']} 个")
    print(f"  音频：{stats['audio']} 个")
    print(f"  总大小：{stats['total_size'] / 1024:.2f} KB")
