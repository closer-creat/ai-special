#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试小说爬虫的错误处理与重试机制
"""

import sys
import os
from unittest.mock import Mock, patch
from novel_crawler import NovelCrawler

class TestNovelCrawler:
    def __init__(self):
        self.crawler = NovelCrawler('https://example.com/novel')
    def test_request_with_retry_success(self):
        """测试请求成功的情况"""
        print("测试请求成功的情况...")
        
        # 创建一个模拟的响应对象
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="chapter-list"><a href="/chapter1">第一章</a></div></body></html>'
        mock_response.raise_for_status = Mock()
        
        # 模拟requests.get方法
        with patch('requests.Session.get', return_value=mock_response):
            response = self.crawler._request_with_retry('https://example.com/novel')
            assert response is not None
            print("✓ 请求成功测试通过")
    def test_request_with_retry_failure(self):
        """测试请求失败的情况"""
        print("测试请求失败的情况...")
        
        # 模拟requests.get方法抛出异常
        with patch('requests.Session.get', side_effect=Exception('网络错误')):
            response = self.crawler._request_with_retry('https://example.com/novel')
            assert response is None
            print("✓ 请求失败测试通过")
    def test_get_novel_chapters(self):
        """测试获取章节列表"""
        print("测试获取章节列表...")
        
        # 创建一个模拟的响应对象
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
        <body>
            <div class="chapter-list">
                <a href="/chapter1">第一章</a>
                <a href="/chapter2">第二章</a>
                <a href="/chapter3">第三章</a>
            </div>
        </body>
        </html>
        '''
        mock_response.raise_for_status = Mock()
        
        # 模拟requests.get方法
        with patch('requests.Session.get', return_value=mock_response):
            chapters = self.crawler.get_novel_chapters()
            assert len(chapters) == 3
            assert chapters[0]['name'] == '第一章'
            assert chapters[0]['url'] == 'https://example.com/novel/chapter1'
            print("✓ 获取章节列表测试通过")
    def test_get_chapter_content(self):
        """测试获取章节内容"""
        print("测试获取章节内容...")
        
        # 创建一个模拟的响应对象
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
        <body>
            <div class="content">
                第一章内容
                这是第一章的正文内容。
            </div>
        </body>
        </html>
        '''
        mock_response.raise_for_status = Mock()
        
        # 模拟requests.get方法
        with patch('requests.Session.get', return_value=mock_response):
            content = self.crawler.get_chapter_content('https://example.com/novel/chapter1')
            assert content is not None
            assert '第一章内容' in content
            print("✓ 获取章节内容测试通过")
    def run_all_tests(self):
        """运行所有测试"""
        print("开始测试小说爬虫...\n")
        
        try:
            self.test_request_with_retry_success()
            self.test_request_with_retry_failure()
            self.test_get_novel_chapters()
            self.test_get_chapter_content()
            print("\n✓ 所有测试通过！")
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            return False
        return True

if __name__ == '__main__':
    tester = TestNovelCrawler()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
