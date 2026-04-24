#!/usr/bin/env python3
"""小说爬虫主入口"""
import argparse
import time
from spiders.novel_spider import NovelSpider

def main():
    parser = argparse.ArgumentParser(description='小说爬虫')
    parser.add_argument('url', help='小说目录页URL')
    parser.add_argument('--format', choices=['docx', 'txt'], default='docx', help='输出格式')
    parser.add_argument('--start', type=int, default=1, help='开始章节')
    parser.add_argument('--end', type=int, help='结束章节')
    parser.add_argument('--force', action='store_true', help='强制覆盖已存在的文件')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("小说爬虫工具")
    print("=" * 60)
    print(f"小说URL: {args.url}")
    print(f"输出格式: {args.format}")
    print(f"开始章节: {args.start}")
    if args.end:
        print(f"结束章节: {args.end}")
    print("=" * 60)
    
    # 验证URL
    spider = NovelSpider(args.url)
    if not spider.validate_url():
        print("错误: 无效的小说网站URL")
        print("支持的网站: 起点中文网 (qidian.com) 和 番茄小说 (fanqie.com)")
        return
    
    # 识别网站类型
    site_type = spider.identify_site()
    if not site_type:
        print("错误: 不支持的网站类型")
        print("支持的网站: 起点中文网 (qidian.com) 和 番茄小说 (fanqie.com)")
        return
    
    print(f"识别到网站类型: {'起点中文网' if site_type == 'qidian' else '番茄小说'}")
    
    # 解析章节列表
    print("正在解析章节列表...")
    if not spider.parse_chapters():
        print("错误: 无法解析章节列表")
        return
    
    print(f"共发现 {len(spider.chapters)} 个章节")
    
    # 确认爬取范围
    start_chapter = args.start - 1  # 转换为0索引
    end_chapter = args.end if args.end else len(spider.chapters)
    
    if start_chapter < 0:
        start_chapter = 0
    if end_chapter > len(spider.chapters):
        end_chapter = len(spider.chapters)
    
    if start_chapter >= end_chapter:
        print("错误: 开始章节大于或等于结束章节")
        return
    
    print(f"爬取范围: 第 {start_chapter + 1} 章 到 第 {end_chapter} 章")
    print(f"共 {end_chapter - start_chapter} 个章节")
    
    # 确认爬取
    if not args.force:
        confirm = input("是否开始爬取？(y/n): ")
        if confirm.lower() != 'y':
            print("爬取已取消")
            return
    
    # 开始爬取
    print("=" * 60)
    print("开始爬取...")
    start_time = time.time()
    
    spider.crawl_novel(
        output_format=args.format,
        start_chapter=start_chapter,
        end_chapter=end_chapter,
        verbose=args.verbose
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"爬取完成，总用时: {total_time:.2f} 秒")
    print("=" * 60)

if __name__ == '__main__':
    main()