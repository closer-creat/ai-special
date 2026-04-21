#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说爬虫使用示例
"""

from novel_crawler import NovelCrawler

if __name__ == '__main__':
    # 示例：爬取笔趣阁的小说
    # 注意：请尊重网站的robots.txt规则，不要过度请求
    base_url = 'https://www.biquge.co/book/12345/'  # 替换为实际的小说URL
    
    # 初始化爬虫，设置最大重试次数为5，重试间隔为3秒
    crawler = NovelCrawler(base_url, max_retries=5, retry_delay=3)
    
    # 开始爬取小说，保存到novel.txt文件
    crawler.crawl_novel(output_file='novel.txt')
