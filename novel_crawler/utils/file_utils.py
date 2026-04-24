import os
from docx import Document

def save_to_docx(title, content_list):
    """保存内容到docx文件"""
    doc = Document()
    doc.add_heading(title, level=0)
    
    for content in content_list:
        # 分离章节标题和内容
        parts = content.split('\n\n', 1)
        if len(parts) == 2:
            chapter_title, chapter_content = parts
            # 添加章节标题
            doc.add_heading(chapter_title, level=1)
            # 添加章节内容，按段落分割
            paragraphs = chapter_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    doc.add_paragraph(para)
        else:
            # 如果没有章节标题，直接添加内容
            doc.add_paragraph(content)
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_path = os.path.join(output_dir, f"{title}.docx")
    doc.save(file_path)
    return file_path

def save_to_txt(title, content_list):
    """保存内容到txt文件"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_path = os.path.join(output_dir, f"{title}.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n\n")
        for content in content_list:
            # 确保章节内容格式正确
            f.write(content)
    
    return file_path