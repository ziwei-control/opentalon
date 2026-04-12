#!/usr/bin/env python3
"""
LLM 调用接口

支持多种 LLM 提供商：
- OpenAI 兼容 API
- 本地模型 (Ollama, LM Studio)
- 自定义端点
"""

import os
import json
import requests
from typing import Optional, Dict, List, Any
from pathlib import Path

class LLMClient:
    """LLM 客户端基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.timeout = config.get('timeout', 60)
        self.max_tokens = config.get('max_tokens', 4096)
        self.temperature = config.get('temperature', 0.7)
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            **kwargs: 额外参数
        
        Returns:
            AI 回复的文本内容
        """
        raise NotImplementedError
    
    def _prepare_headers(self) -> Dict:
        """准备请求头"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def _prepare_payload(self, messages: List[Dict], **kwargs) -> Dict:
        """准备请求体"""
        return {
            'model': self.model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'temperature': kwargs.get('temperature', self.temperature),
            'stream': False
        }


class OpenAICompatibleClient(LLMClient):
    """OpenAI 兼容 API 客户端"""
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = self._prepare_headers()
        payload = self._prepare_payload(messages, **kwargs)
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            return f"❌ LLM 请求失败：{str(e)}"


class OllamaClient(LLMClient):
    """Ollama 本地模型客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama2')
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        url = f"{self.base_url}/api/chat"
        
        # Ollama 格式转换
        ollama_messages = []
        system_prompt = ""
        
        for msg in messages:
            if msg['role'] == 'system':
                system_prompt = msg['content']
            else:
                ollama_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        payload = {
            'model': self.model,
            'messages': ollama_messages,
            'stream': False
        }
        
        if system_prompt:
            payload['system'] = system_prompt
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data['message']['content']
            
        except requests.exceptions.RequestException as e:
            return f"❌ Ollama 请求失败：{str(e)}"


class LMStudioClient(LLMClient):
    """LM Studio 本地模型客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:1234/v1')
        self.model = config.get('model', 'local-model')
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        # LM Studio 使用 OpenAI 兼容格式
        return OpenAICompatibleClient(self.config).chat(messages, **kwargs)


def create_llm_client(config_path: Optional[str] = None) -> LLMClient:
    """
    根据配置创建 LLM 客户端
    
    Args:
        config_path: 配置文件路径，默认使用 ~/.opentalon/llm_config.json
    
    Returns:
        LLMClient 实例
    """
    if config_path is None:
        config_path = os.path.expanduser('~/.opentalon/llm_config.json')
    
    # 加载配置
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        # 默认配置
        config = {
            'provider': 'openai',
            'api_key': os.environ.get('OPENAI_API_KEY', ''),
            'base_url': 'https://api.openai.com/v1',
            'model': 'gpt-3.5-turbo'
        }
    
    provider = config.get('provider', 'openai').lower()
    
    if provider == 'ollama':
        return OllamaClient(config)
    elif provider == 'lmstudio':
        return LMStudioClient(config)
    else:
        return OpenAICompatibleClient(config)


def load_context(workspace_path: str) -> str:
    """
    加载工作空间上下文
    
    Args:
        workspace_path: 工作空间路径
    
    Returns:
        格式化的上下文字符串
    """
    context_parts = []
    
    # 加载 SOUL.md
    soul_path = Path(workspace_path) / 'SOUL.md'
    if soul_path.exists():
        with open(soul_path, 'r', encoding='utf-8') as f:
            context_parts.append(f"## 智能体人格\n\n{f.read()}")
    
    # 加载 USER.md
    user_path = Path(workspace_path) / 'USER.md'
    if user_path.exists():
        with open(user_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 只取前 2000 字符避免过长
            if len(content) > 2000:
                content = content[:2000] + "\n...(省略)"
            context_parts.append(f"## 用户偏好\n\n{content}")
    
    # 加载 MEMORY.md
    memory_path = Path(workspace_path) / 'MEMORY.md'
    if memory_path.exists():
        with open(memory_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) > 3000:
                content = content[:3000] + "\n...(省略)"
            context_parts.append(f"## 长期记忆\n\n{content}")
    
    return '\n\n'.join(context_parts)


def build_messages(user_input: str, context: str, system_prompt: str = "") -> List[Dict]:
    """
    构建消息列表
    
    Args:
        user_input: 用户输入
        context: 上下文信息
        system_prompt: 系统提示
    
    Returns:
        消息列表
    """
    messages = []
    
    # 系统提示
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    
    # 上下文
    if context:
        messages.append({
            'role': 'system',
            'content': f"以下是相关上下文信息：\n\n{context}"
        })
    
    # 用户输入
    messages.append({'role': 'user', 'content': user_input})
    
    return messages


# 主函数 - 测试用
if __name__ == "__main__":
    import sys
    
    print("🤖 OpenTalon LLM 接口测试")
    print("")
    
    # 创建客户端
    client = create_llm_client()
    
    print(f"提供商：{client.config.get('provider', 'unknown')}")
    print(f"模型：{client.model}")
    print(f"端点：{client.base_url}")
    print("")
    
    # 测试对话
    test_message = "你好，请简单介绍一下自己"
    print(f"用户：{test_message}")
    print("")
    
    messages = build_messages(test_message, context="")
    response = client.chat(messages)
    
    print(f"AI: {response}")
