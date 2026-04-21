from spiders.base_spider import BaseSpider
from utils.file_utils import save_to_docx, save_to_txt
from tqdm import tqdm
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class NovelSpider(BaseSpider):
    def __init__(self, novel_url):
        super().__init__()
        self.novel_url = novel_url
        self.chapters = []
        self.site_type = None
        self.novel_title = None
        self.novel_author = None
    
    def validate_url(self):
        """验证URL是否为有效的小说网站URL"""
        patterns = [
            r'^https?://.*qidian\.com.*',  # 起点中文网
            r'^https?://.*fanqie\.com.*'   # 番茄小说
        ]
        
        for pattern in patterns:
            if re.match(pattern, self.novel_url):
                return True
        return False
    
    def identify_site(self):
        """识别网站类型"""
        if 'qidian.com' in self.novel_url:
            self.site_type = 'qidian'
            return 'qidian'
        elif 'fanqie.com' in self.novel_url:
            self.site_type = 'fanqie'
            return 'fanqie'
        else:
            return None
    
    def parse_chapters(self):
        """根据网站类型解析章节列表"""
        if not self.validate_url():
            print("无效的小说网站URL")
            return False
        
        site_type = self.identify_site()
        if not site_type:
            print("不支持的网站类型")
            return False
        
        if site_type == 'qidian':
            return self._parse_qidian_chapters()
        elif site_type == 'fanqie':
            return self._parse_fanqie_chapters()
    
    def _parse_qidian_chapters(self):
        """解析起点中文网章节列表"""
        # 使用selenium获取页面，因为起点有反爬
        html = self.get_html(self.novel_url, use_selenium=True)
        soup = self.get_soup(html)
        
        if not soup:
            return False
        
        # 获取小说标题
        title_elem = soup.find('h1', class_='book-info__title')
        if title_elem:
            self.novel_title = title_elem.text.strip()
        
        # 获取作者信息
        author_elem = soup.find('a', class_='writer')
        if author_elem:
            self.novel_author = author_elem.text.strip()
        
        # 解析章节列表
        chapter_list = soup.find('ul', class_='chapter__list')
        if chapter_list:
            for chapter in chapter_list.find_all('li'):
                a_tag = chapter.find('a')
                if a_tag:
                    chapter_title = a_tag.text.strip()
                    chapter_url = a_tag.get('href')
                    if chapter_url and not chapter_url.startswith('http'):
                        chapter_url = 'https:' + chapter_url
                    self.chapters.append({'title': chapter_title, 'url': chapter_url})
        
        return len(self.chapters) > 0
    
    def _parse_fanqie_chapters(self):
        """解析番茄小说章节列表"""
        html = self.get_html(self.novel_url, use_selenium=True)
        soup = self.get_soup(html)
        
        if not soup:
            return False
        
        # 获取小说标题
        title_elem = soup.find('h1', class_='book-name')
        if title_elem:
            self.novel_title = title_elem.text.strip()
        
        # 获取作者信息
        author_elem = soup.find('a', class_='author-name')
        if author_elem:
            self.novel_author = author_elem.text.strip()
        
        # 解析章节列表
        chapter_list = soup.find('div', class_='chapter-list')
        if chapter_list:
            for chapter in chapter_list.find_all('a'):
                chapter_title = chapter.text.strip()
                chapter_url = chapter.get('href')
                if chapter_url and not chapter_url.startswith('http'):
                    chapter_url = 'https://fanqie.com' + chapter_url
                self.chapters.append({'title': chapter_title, 'url': chapter_url})
        
        return len(self.chapters) > 0
    
    def crawl_novel(self, output_format='docx', start_chapter=0, end_chapter=None, verbose=False):
        if not self.chapters:
            if not self.parse_chapters():
                print("无法解析章节列表")
                return
        
        # 确定爬取范围
        if end_chapter is None:
            end_chapter = len(self.chapters)
        
        # 截取章节范围
        chapters_to_crawl = self.chapters[start_chapter:end_chapter]
        total_chapters = len(chapters_to_crawl)
        
        if total_chapters == 0:
            print("没有章节需要爬取")
            return
        
        novel_content = []
        start_time = time.time()
        
        # 使用多线程爬取章节内容
        max_workers = min(5, total_chapters)  # 限制并发数，避免被封
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_chapter = {executor.submit(self._crawl_chapter, chapter): chapter for chapter in chapters_to_crawl}
            
            # 处理结果
            for i, future in enumerate(tqdm(as_completed(future_to_chapter), total=total_chapters, desc="爬取章节")):
                chapter = future_to_chapter[future]
                try:
                    chapter_content = future.result()
                    if chapter_content:
                        novel_content.append(f"{chapter['title']}\n\n{chapter_content}\n\n")
                except Exception as e:
                    print(f"爬取章节 {chapter['title']} 失败: {e}")
                
                # 显示进度和预估时间
                if i > 0:
                    elapsed_time = time.time() - start_time
                    avg_time_per_chapter = elapsed_time / (i + 1)
                    remaining_chapters = total_chapters - (i + 1)
                    estimated_remaining_time = avg_time_per_chapter * remaining_chapters
                    
                    if verbose:
                        print(f"\r进度: {i + 1}/{total_chapters} 章, 预计剩余时间: {estimated_remaining_time:.2f} 秒", end="")
        
        # 按章节顺序排序
        chapter_title_to_content = {content.split('\n\n')[0]: content for content in novel_content}
        sorted_content = []
        for chapter in chapters_to_crawl:
            if chapter['title'] in chapter_title_to_content:
                sorted_content.append(chapter_title_to_content[chapter['title']])
        
        if sorted_content:
            # 生成文件名：书名_作者
            novel_title = self.novel_title or (self.chapters[0]['title'].split(' ')[0] if self.chapters else 'novel')
            novel_author = self.novel_author or '未知作者'
            file_name = f"{novel_title}_{novel_author}"
            # 清理文件名中的特殊字符
            file_name = re.sub(r'[\\/:*?"<>|]', '', file_name)
            
            if output_format == 'docx':
                save_to_docx(file_name, sorted_content)
            else:
                save_to_txt(file_name, sorted_content)
            print(f"小说爬取完成，已保存为 {file_name}.{output_format}")
        else:
            print("未爬取到任何内容")
        
        # 关闭selenium driver
        self.close_driver()
    
    def _crawl_chapter(self, chapter):
        """爬取章节内容"""
        html = self.get_html(chapter['url'], use_selenium=True)
        soup = self.get_soup(html)
        
        if not soup:
            return None
        
        if self.site_type == 'qidian':
            return self._parse_qidian_content(soup)
        elif self.site_type == 'fanqie':
            return self._parse_fanqie_content(soup)
        return None
    
    def _parse_qidian_content(self, soup):
        """解析起点中文网章节内容"""
        # 处理分页加载的情况
        content_div = soup.find('div', class_='read-content j_readContent')
        if content_div:
            # 移除不需要的元素
            for script in content_div.find_all('script'):
                script.decompose()
            for style in content_div.find_all('style'):
                style.decompose()
            for ad in content_div.find_all(class_=['read-ad', 'advertisement']):
                ad.decompose()
            
            content = content_div.get_text(separator='\n', strip=True)
            # 清洗内容
            content = self._clean_content(content)
            return content
        return None
    
    def _parse_fanqie_content(self, soup):
        """解析番茄小说章节内容"""
        # 处理分页加载的情况
        content_div = soup.find('div', class_='read-content')
        if content_div:
            # 移除不需要的元素
            for script in content_div.find_all('script'):
                script.decompose()
            for style in content_div.find_all('style'):
                style.decompose()
            for ad in content_div.find_all(class_=['read-ad', 'advertisement']):
                ad.decompose()
            
            content = content_div.get_text(separator='\n', strip=True)
            # 清洗内容
            content = self._clean_content(content)
            return content
        return None
    
    def _clean_content(self, content):
        """清洗章节内容"""
        # 移除多余的空行
        content = re.sub(r'\n\s*\n', '\n\n', content)
        # 移除广告内容
        ad_patterns = [
            r'[\s\S]*?本书由[\s\S]*?授权起点中文网首发',
            r'[\s\S]*?请记住本书首发域名：[\s\S]*?',
            r'[\s\S]*?手机版阅读网址：[\s\S]*?',
            r'[\s\S]*?更多精彩内容请关注起点读书[\s\S]*?',
            r'[\s\S]*?番茄小说网[\s\S]*?',
            r'[\s\S]*?广告[\s\S]*?',
            r'[\s\S]*?推荐阅读[\s\S]*?',
            r'[\s\S]*?加入书架[\s\S]*?',
            r'[\s\S]*?收藏[\s\S]*?'
        ]
        for pattern in ad_patterns:
            content = re.sub(pattern, '', content)
        # 移除首尾空白
        content = content.strip()
        return content