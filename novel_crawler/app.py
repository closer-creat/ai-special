#!/usr/bin/env python3
"""小说爬虫Web界面"""
from flask import Flask, render_template, request, jsonify, send_file
import sys
sys.path.append('/workspace/novel_crawler')
from spiders.novel_spider import NovelSpider
import os
import threading
import queue
import time

app = Flask(__name__)

# 爬取任务状态
task_status = {}

class CrawlTask:
    def __init__(self, task_id, url, output_format, start_chapter, end_chapter):
        self.task_id = task_id
        self.url = url
        self.output_format = output_format
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.status = "pending"
        self.progress = 0
        self.total_chapters = 0
        self.current_chapter = 0
        self.estimated_time = 0
        self.file_path = None
        self.error = None

    def update_progress(self, current, total, estimated_time):
        self.current_chapter = current
        self.total_chapters = total
        self.progress = int((current / total) * 100) if total > 0 else 0
        self.estimated_time = estimated_time

    def set_status(self, status):
        self.status = status

    def set_file_path(self, file_path):
        self.file_path = file_path

    def set_error(self, error):
        self.error = error

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "current_chapter": self.current_chapter,
            "total_chapters": self.total_chapters,
            "estimated_time": self.estimated_time,
            "file_path": self.file_path,
            "error": self.error
        }

def crawl_worker(task):
    """爬取任务工作线程"""
    try:
        task.set_status("running")
        
        # 初始化爬虫
        spider = NovelSpider(task.url)
        
        # 验证URL
        if not spider.validate_url():
            task.set_error("无效的小说网站URL")
            task.set_status("failed")
            return
        
        # 识别网站类型
        site_type = spider.identify_site()
        if not site_type:
            task.set_error("不支持的网站类型")
            task.set_status("failed")
            return
        
        # 解析章节列表
        if not spider.parse_chapters():
            task.set_error("无法解析章节列表")
            task.set_status("failed")
            return
        
        # 确定爬取范围
        start_chapter = task.start_chapter - 1  # 转换为0索引
        end_chapter = task.end_chapter if task.end_chapter else len(spider.chapters)
        
        if start_chapter < 0:
            start_chapter = 0
        if end_chapter > len(spider.chapters):
            end_chapter = len(spider.chapters)
        
        if start_chapter >= end_chapter:
            task.set_error("开始章节大于或等于结束章节")
            task.set_status("failed")
            return
        
        # 更新任务信息
        total_chapters = end_chapter - start_chapter
        task.total_chapters = total_chapters
        
        # 开始爬取
        novel_content = []
        start_time = time.time()
        
        for i, chapter in enumerate(spider.chapters[start_chapter:end_chapter]):
            chapter_content = spider._crawl_chapter(chapter)
            if chapter_content:
                novel_content.append(f"{chapter['title']}\n\n{chapter_content}\n\n")
            
            # 更新进度
            elapsed_time = time.time() - start_time
            avg_time_per_chapter = elapsed_time / (i + 1)
            remaining_chapters = total_chapters - (i + 1)
            estimated_remaining_time = avg_time_per_chapter * remaining_chapters
            
            task.update_progress(i + 1, total_chapters, estimated_remaining_time)
        
        if novel_content:
            # 生成文件名：书名_作者
            novel_title = spider.novel_title or (spider.chapters[0]['title'].split(' ')[0] if spider.chapters else 'novel')
            novel_author = spider.novel_author or '未知作者'
            file_name = f"{novel_title}_{novel_author}"
            # 清理文件名中的特殊字符
            import re
            file_name = re.sub(r'[\\/:*?"<>|]', '', file_name)
            
            if task.output_format == 'docx':
                from utils.file_utils import save_to_docx
                file_path = save_to_docx(file_name, novel_content)
            else:
                from utils.file_utils import save_to_txt
                file_path = save_to_txt(file_name, novel_content)
            
            task.set_file_path(file_path)
            task.set_status("completed")
        else:
            task.set_error("未爬取到任何内容")
            task.set_status("failed")
            
    except Exception as e:
        task.set_error(f"爬取过程中发生错误: {str(e)}")
        task.set_status("failed")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/crawl', methods=['POST'])
def start_crawl():
    """开始爬取任务"""
    data = request.json
    url = data.get('url')
    output_format = data.get('format', 'docx')
    start_chapter = data.get('start', 1)
    end_chapter = data.get('end')
    
    if not url:
        return jsonify({"error": "请提供小说URL"}), 400
    
    # 生成任务ID
    import uuid
    task_id = str(uuid.uuid4())
    
    # 创建任务
    task = CrawlTask(task_id, url, output_format, start_chapter, end_chapter)
    task_status[task_id] = task
    
    # 启动爬取线程
    thread = threading.Thread(target=crawl_worker, args=(task,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"task_id": task_id})

@app.route('/api/status/<task_id>')
def get_status(task_id):
    """获取任务状态"""
    if task_id not in task_status:
        return jsonify({"error": "任务不存在"}), 404
    
    task = task_status[task_id]
    return jsonify(task.to_dict())

@app.route('/api/download/<task_id>')
def download_file(task_id):
    """下载爬取结果"""
    if task_id not in task_status:
        return jsonify({"error": "任务不存在"}), 404
    
    task = task_status[task_id]
    if task.status != "completed" or not task.file_path:
        return jsonify({"error": "任务未完成或无下载文件"}), 400
    
    if not os.path.exists(task.file_path):
        return jsonify({"error": "文件不存在"}), 404
    
    return send_file(task.file_path, as_attachment=True)

if __name__ == '__main__':
    # 创建templates目录
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # 创建data目录
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    app.run(debug=True, host='0.0.0.0', port=5000)