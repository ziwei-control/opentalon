#!/usr/bin/env python3
"""
OpenTalon 实时联网搜索模块
支持：
- DuckDuckGo 搜索（免费，无需 API Key）
- 新闻获取
- 网页内容抓取
- 实时数据整合
"""

import requests
from typing import List, Dict, Optional
import re
from html import unescape
from datetime import datetime
from bs4 import BeautifulSoup


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
        # 使用 DuckDuckGo HTML 搜索
        url = 'https://html.duckduckgo.com/html/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        data = {'q': query, 'kl': 'zh-cn'}
        
        response = requests.post(url, headers=headers, data=data, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        # 使用 BeautifulSoup 解析
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # 查找所有结果块
        result_divs = soup.find_all('div', class_='result')
        
        for div in result_divs[:num_results * 2]:
            # 提取标题链接
            title_link = div.find('a', class_='result__a')
            if not title_link:
                continue
            
            title = title_link.get_text(strip=True)
            # 跳过太短的标题
            if len(title) < 20:
                continue
            
            # 提取 URL
            raw_url = title_link.get('href', '')
            
            # DuckDuckGo 使用重定向 URL，需要提取真实 URL
            if raw_url.startswith('/'):
                # 从 onclick 属性中提取
                onclick = title_link.get('onclick', '')
                import re
                match = re.search(r"r='(https?://[^']+)'", onclick)
                if match:
                    raw_url = match.group(1)
                else:
                    continue  # 无法提取 URL，跳过
            
            # 提取摘要
            snippet_elem = div.find('a', class_='result__snippet')
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
            
            # 过滤 DuckDuckGo 自己的链接
            if 'duckduckgo' in raw_url.lower():
                continue
            
            results.append({
                'title': title,
                'url': raw_url,
                'snippet': snippet,
                'timestamp': datetime.now().isoformat()
            })
            
            if len(results) >= num_results:
                break
        
        if not results:
            return [{
                'title': '搜索完成',
                'url': '',
                'snippet': f'未找到关于 "{query}" 的具体结果，但 AI 助手会尽力回答您的问题。',
                'timestamp': datetime.now().isoformat()
            }]
        
        return results
        
    except Exception as e:
        print(f"搜索错误：{e}")
        return [{
            'title': '搜索暂时不可用',
            'url': '',
            'snippet': f'搜索服务暂时无法使用：{str(e)}。但 AI 助手仍会尽力回答您的问题。',
            'timestamp': datetime.now().isoformat()
        }]


def search_news(query: str = '今日新闻', num_results: int = 5) -> List[Dict]:
    """
    搜索新闻
    
    Args:
        query: 新闻关键词
        num_results: 返回结果数量
    
    Returns:
        新闻列表
    """
    # 使用普通搜索，但添加 news 关键词
    return search_web(f"news {query}", num_results)


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


def get_realtime_context(query: str, max_results: int = 3) -> str:
    """
    获取实时上下文信息
    
    Args:
        query: 查询关键词
        max_results: 最大结果数
    
    Returns:
        格式化的实时信息字符串
    """
    context_parts = []
    
    # 添加时间戳
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    context_parts.append(f" 当前时间：{current_time}")
    
    # 执行搜索
    results = search_web(query, num_results=max_results)
    
    if results and 'error' not in results[0].get('title', ''):
        context_parts.append("\n\n📊 实时搜索结果：")
        for i, r in enumerate(results, 1):
            if 'title' in r and 'url' in r:
                context_parts.append(f"\n{i}. {r['title']}")
                if r.get('url'):
                    context_parts.append(f"   来源：{r['url']}")
    
    return '\n'.join(context_parts)
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
