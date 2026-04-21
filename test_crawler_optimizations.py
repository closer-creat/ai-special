#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试小说爬虫的优化效果
"""

import sys
import os
import time
from novel_crawler.spiders.novel_spider import NovelSpider

class TestCrawlerOptimizations:
    def __init__(self):
        # 使用一个模拟的URL进行测试
        self.test_url = "https://www.fanqie.com/book/10169298360043904"
        self.spider = NovelSpider(self.test_url)
    def test_site_identification(self):
        """测试网站识别功能"""
        print("测试网站识别功能...")
        site_type = self.spider.identify_site()
        assert site_type == 'fanqie', f"期望识别为 'fanqie'，实际识别为 '{site_type}'"
        print("✓ 网站识别测试通过")
    def test_url_validation(self):
        """测试URL验证功能"""
        print("测试URL验证功能...")
        is_valid = self.spider.validate_url()
        assert is_valid, "期望URL有效，实际无效"
        print("✓ URL验证测试通过")
    def test_multi_threading(self):
        """测试多线程爬取功能"""
        print("测试多线程爬取功能...")
        # 模拟章节数据
        self.spider.chapters = [
            {'title': '第一章', 'url': 'https://www.fanqie.com/chapter/1'},
            {'title': '第二章', 'url': 'https://www.fanqie.com/chapter/2'},
            {'title': '第三章', 'url': 'https://www.fanqie.com/chapter/3'}
        ]
        self.spider.site_type = 'fanqie'
        self.spider.novel_title = '测试小说'
        self.spider.novel_author = '测试作者'
        
        # 测试多线程爬取
        start_time = time.time()
        self.spider.crawl_novel(output_format='txt', start_chapter=0, end_chapter=3, verbose=True)
        end_time = time.time()
        print(f"多线程爬取用时: {end_time - start_time:.2f} 秒")
        print("✓ 多线程爬取测试通过")
    def run_all_tests(self):
        """运行所有测试"""
        print("开始测试小说爬虫优化效果...\n")
        
        try:
            self.test_site_identification()
            self.test_url_validation()
            self.test_multi_threading()
            print("\n✓ 所有测试通过！")
            return True
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            return False

if __name__ == '__main__':
    tester = TestCrawlerOptimizations()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
