#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说爬虫，实现错误处理与重试机制
"""

import requests
import time
import logging
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('novel_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('novel_crawler')

class NovelCrawler:
    def __init__(self, base_url: str, max_retries: int = 3, retry_delay: int = 2):
        """
        初始化小说爬虫
        
        Args:
            base_url: 小说网站的基础URL
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
        """
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        # 设置请求头
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    def _request_with_retry(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        带重试机制的网络请求
        
        Args:
            url: 请求URL
            method: 请求方法
            **kwargs: 其他请求参数
            
        Returns:
            请求响应对象，如果失败则返回None
        """
        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, **kwargs, timeout=10)
                elif method.upper() == 'POST':
                    response = self.session.post(url, **kwargs, timeout=10)
                else:
                    logger.error(f"不支持的请求方法: {method}")
                    return None
                
                # 检查响应状态码
                response.raise_for_status()
                logger.info(f"请求成功: {url}")
                return response
            except Exception as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {url}, 错误: {str(e)}")
                if attempt < self.max_retries - 1:
                    # 指数退避策略
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"等待 {delay:.2f} 秒后重试...")
                    time.sleep(delay)
                else:
                    logger.error(f"多次请求失败: {url}, 错误: {str(e)}")
                    return None
    def get_novel_chapters(self) -> List[Dict[str, str]]:
        """
        获取小说章节列表
        
        Returns:
            章节列表，每个元素包含章节名称和链接
        """
        try:
            response = self._request_with_retry(self.base_url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # 这里需要根据具体网站结构调整选择器
            # 示例：假设章节列表在class为chapter-list的div中
            chapter_elements = soup.select('.chapter-list a')
            
            chapters = []
            for element in chapter_elements:
                chapter_name = element.text.strip()
                chapter_url = element.get('href')
                if chapter_url and not chapter_url.startswith('http'):
                    chapter_url = self.base_url + chapter_url
                chapters.append({'name': chapter_name, 'url': chapter_url})
            
            logger.info(f"成功获取 {len(chapters)} 个章节")
            return chapters
        except Exception as e:
            logger.error(f"获取章节列表失败: {str(e)}")
            return []
    def get_chapter_content(self, chapter_url: str) -> Optional[str]:
        """
        获取章节内容
        
        Args:
            chapter_url: 章节URL
            
        Returns:
            章节内容，如果失败则返回None
        """
        try:
            response = self._request_with_retry(chapter_url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # 这里需要根据具体网站结构调整选择器
            # 示例：假设章节内容在class为content的div中
            content_element = soup.select_one('.content')
            if not content_element:
                logger.warning(f"未找到章节内容: {chapter_url}")
                return None
            
            # 提取内容并清理
            content = content_element.text.strip()
            # 移除可能的广告和无关内容
            content = '\n'.join([line for line in content.split('\n') if line.strip()])
            
            logger.info(f"成功获取章节内容: {chapter_url}")
            return content
        except Exception as e:
            logger.error(f"获取章节内容失败: {chapter_url}, 错误: {str(e)}")
            return None
    def crawl_novel(self, output_file: str = 'novel.txt'):
        """
        爬取整本小说
        
        Args:
            output_file: 输出文件名
        """
        try:
            logger.info(f"开始爬取小说: {self.base_url}")
            
            # 获取章节列表
            chapters = self.get_novel_chapters()
            if not chapters:
                logger.error("获取章节列表失败，无法继续爬取")
                return
            
            # 爬取每个章节内容
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, chapter in enumerate(chapters, 1):
                    logger.info(f"爬取第 {i}/{len(chapters)} 章: {chapter['name']}")
                    
                    content = self.get_chapter_content(chapter['url'])
                    if content:
                        # 写入章节标题和内容
                        f.write(f"\n{'='*50}\n")
                        f.write(f"{chapter['name']}\n")
                        f.write(f"{'='*50}\n")
                        f.write(content)
                        f.write("\n")
                    else:
                        logger.error(f"跳过章节: {chapter['name']}")
                    
                    # 避免请求过于频繁
                    time.sleep(random.uniform(0.5, 2))
            
            logger.info(f"小说爬取完成，已保存到: {output_file}")
        except Exception as e:
            logger.error(f"爬取小说失败: {str(e)}")

if __name__ == '__main__':
    # 示例使用
    # 注意：请替换为实际的小说网站URL
    base_url = 'https://example.com/novel'
    crawler = NovelCrawler(base_url)
    crawler.crawl_novel()
