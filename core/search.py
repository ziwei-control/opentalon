#!/usr/bin/env python3
"""
OpenTalon 联网搜索模块
支持：
- DuckDuckGo 搜索（免费，无需 API Key）
- 新闻获取
- 网页内容抓取
"""

import requests
from typing import List, Dict
import re
from html import unescape


def search_web(query: str, num_results: int = 5) -> List[Dict]:
    """
    使用 DuckDuckGo 搜索网页
    
    Args:
        query: 搜索关键词
        num_results: 返回结果数量
    
    Returns:
        搜索结果列表
    """
    try:
        # DuckDuckGo HTML 搜索
        url = 'https://html.duckduckgo.com/html/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        data = {'q': query}
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        
        results = []
        html = response.text
        
        # 解析搜索结果
        import re
        pattern = r'<a class="result__a" href="([^"]+)">([^<]+)</a>'
        matches = re.findall(pattern, html)
        
        for i, (url, title) in enumerate(matches[:num_results]):
            # 清理 URL
            if url.startswith('//'):
                url = 'https:' + url
            
            results.append({
                'title': unescape(title),
                'url': url,
                'snippet': get_snippet(html, title)
            })
        
        return results if results else [{'error': '未找到搜索结果'}]
        
    except Exception as e:
        return [{'error': f'搜索失败：{str(e)}'}]


def get_snippet(html: str, title: str) -> str:
    """从 HTML 中提取摘要"""
    try:
        # 简单实现，返回标题附近的文本
        idx = html.find(title)
        if idx > 0:
            snippet = html[max(0, idx-100):idx+200]
            # 清理 HTML 标签
            snippet = re.sub(r'<[^>]+>', ' ', snippet)
            snippet = unescape(snippet).strip()
            return snippet[:150] + '...' if len(snippet) > 150 else snippet
    except:
        pass
    return ''


def search_news(query: str = '今日新闻', num_results: int = 5) -> List[Dict]:
    """
    搜索新闻
    
    Args:
        query: 新闻关键词
        num_results: 返回结果数量
    
    Returns:
        新闻列表
    """
    try:
        # 使用 DuckDuckGo 搜索新闻
        url = 'https://html.duckduckgo.com/html/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        data = {'q': f'news {query}'}
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        
        results = []
        html = response.text
        
        # 解析新闻结果
        pattern = r'<a class="result__a" href="([^"]+)">([^<]+)</a>'
        matches = re.findall(pattern, html)
        
        for url, title in matches[:num_results]:
            if url.startswith('//'):
                url = 'https:' + url
            
            results.append({
                'title': unescape(title),
                'url': url,
                'source': 'News'
            })
        
        return results if results else [{'error': '未找到新闻'}]
        
    except Exception as e:
        return [{'error': f'新闻搜索失败：{str(e)}'}]


def fetch_webpage_content(url: str) -> str:
    """
    抓取网页内容
    
    Args:
        url: 网页 URL
    
    Returns:
        网页文本内容
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 提取文本内容
        html = response.text
        # 清理 HTML 标签
        text = re.sub(r'<[^>]+>', ' ', html)
        text = unescape(text)
        # 清理多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:2000]  # 限制长度
        
    except Exception as e:
        return f'抓取失败：{str(e)}'


def search_with_summary(query: str, search_first: bool = True) -> str:
    """
    搜索并生成摘要
    
    Args:
        query: 搜索关键词
        search_first: 是否先搜索再总结
    
    Returns:
        搜索结果摘要
    """
    # 执行搜索
    results = search_web(query, num_results=5)
    
    if not results or 'error' in results[0]:
        return f"搜索失败：{results[0].get('error', '未知错误')}"
    
    # 构建摘要
    summary = f"🔍 关于 \"{query}\" 的搜索结果：\n\n"
    
    for i, result in enumerate(results, 1):
        if 'error' not in result:
            summary += f"{i}. **{result['title']}**\n"
            summary += f"   URL: {result['url']}\n"
            if result.get('snippet'):
                summary += f"   {result['snippet']}\n\n"
    
    return summary


# 测试
if __name__ == '__main__':
    print("测试搜索功能...")
    
    # 测试网页搜索
    print("\n📄 网页搜索测试:")
    results = search_web("AI 最新消息")
    for r in results[:3]:
        print(f"  - {r.get('title', 'N/A')}")
    
    # 测试新闻搜索
    print("\n📰 新闻搜索测试:")
    news = search_news("今日科技新闻")
    for n in news[:3]:
        print(f"  - {n.get('title', 'N/A')}")
    
    print("\n✅ 搜索模块测试完成")
