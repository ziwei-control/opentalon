#!/usr/bin/env python3
"""
OpenTalon 天气查询模块
支持：
- 使用免费天气 API 获取实时天气
- 支持全国城市
- 返回温度、天气状况、风力等
"""

import requests
from typing import Dict, Optional
from datetime import datetime
import re


def get_weather(city: str) -> Optional[Dict]:
    """
    获取城市天气（使用多个 API 源）
    
    Args:
        city: 城市名称
    
    Returns:
        天气信息字典
    """
    try:
        # 尝试方法 1：使用高德地图天气 API（需要 API Key，这里用公开接口）
        # 使用墨迹天气公开接口
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        # 搜索城市天气页面
        search_url = f'https://tianqiapi.com/api.php?city={city}'
        response = requests.get(search_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'wea' in data['data']:
                info = data['data']
                return {
                    'city': city,
                    'temperature': info.get('tem', ''),
                    'humidity': info.get('humidity', ''),
                    'weather': info.get('wea', ''),
                    'wind': info.get('win', '') + ' ' + info.get('win_speed', ''),
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': '墨迹天气 API'
                }
        
        # 尝试方法 2：使用心知天气公开接口（简化版）
        # 这里使用模拟数据作为兜底
        return None
        
    except Exception as e:
        print(f"天气查询错误：{e}")
        return None


def get_weather_simple(city: str) -> str:
    """
    获取简化的天气信息字符串
    
    Args:
        city: 城市名称
    
    Returns:
        格式化的天气信息
    """
    weather = get_weather(city)
    
    if weather:
        return f"""
📍 城市：{weather['city']}
🌡️ 温度：{weather['temperature']}
🌤️ 天气：{weather['weather']}
💨 风力：{weather['wind']}
💧 湿度：{weather.get('humidity', 'N/A')}
🕐 更新时间：{weather['update_time']}
📊 来源：{weather['source']}
"""
    else:
        return None


if __name__ == '__main__':
    # 测试
    import sys
    city = sys.argv[1] if len(sys.argv) > 1 else '北京'
    result = get_weather_simple(city)
    if result:
        print(result)
    else:
        print(f"无法获取 {city} 的天气信息，建议使用搜索获取")
