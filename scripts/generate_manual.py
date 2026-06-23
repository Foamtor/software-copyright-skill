#!/usr/bin/env python3
"""
生成说明书章节脚本
根据内容JSON和截图，生成说明书章节Word文档
"""

import os
import json
import argparse
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def create_chapter_document():
    """创建新的章节文档"""
    doc = Document()
    
    # 设置默认字体
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(10.5)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    
    # 设置段落格式
    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = 1.5
    paragraph_format.first_line_indent = Cm(0.74)  # 约2字符
    
    return doc

def add_heading(doc, text, level=1):
    """添加标题"""
    heading = doc.add_heading(text, level=level)
    
    # 设置中文字体
    for run in heading.runs:
        run.font.name = '黑体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        
        if level == 1:
            run.font.size = Pt(16)
        elif level == 2:
            run.font.size = Pt(14)
        elif level == 3:
            run.font.size = Pt(12)
    
    return heading

def add_paragraph(doc, text, bold_prefix=None):
    """添加正文段落"""
    para = doc.add_paragraph()
    
    if bold_prefix:
        # 添加加粗前缀
        run = para.add_run(bold_prefix)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        
        # 添加正文
        run = para.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    else:
        run = para.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    
    return para

def add_image(doc, image_path, width=Inches(5), caption=None):
    """添加图片"""
    if not os.path.exists(image_path):
        print(f"警告：图片不存在 {image_path}")
        return None
    
    # 添加图片
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run()
    run.add_picture(image_path, width=width)
    
    # 添加图片说明
    if caption:
        caption_para = doc.add_paragraph()
        caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = caption_para.add_run(caption)
        run.font.size = Pt(9)
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    
    return para

def process_chapter_content(doc, content, images_dir=None):
    """处理章节内容"""
    for key, value in content.items():
        if key == '截图':
            # 处理截图列表
            if isinstance(value, list):
                for img_info in value:
                    img_path = img_info.get('图片', '')
                    if images_dir and not os.path.isabs(img_path):
                        img_path = os.path.join(images_dir, img_path)
                    
                    caption = img_info.get('说明', None)
                    add_image(doc, img_path, caption=caption)
            continue
        
        # 判断标题级别
        if key.startswith('一、') or key.startswith('二、') or key.startswith('三、'):
            # 一级标题
            add_heading(doc, key, level=1)
        elif key.startswith('（') and key.endswith('）'):
            # 二级标题
            add_heading(doc, key, level=2)
        elif key[0:1].isdigit() and key[1:2] in ['.', '、', '.']:
            # 三级标题
            add_heading(doc, key, level=3)
        else:
            # 普通段落或子内容
            if isinstance(value, str):
                # 检查是否包含 [截图: xxx] 标记
                if '[截图:' in value:
                    parts = value.split('[截图:')
                    for i, part in enumerate(parts):
                        if i > 0:
                            # 提取截图信息
                            img_end = part.find(']')
                            if img_end > 0:
                                img_name = part[:img_end].strip()
                                remaining = part[img_end + 1:]
                                
                                # 插入图片
                                img_path = img_name
                                if images_dir and not os.path.isabs(img_path):
                                    img_path = os.path.join(images_dir, img_path)
                                add_image(doc, img_path)
                                
                                # 添加剩余文字
                                if remaining.strip():
                                    add_paragraph(doc, remaining.strip())
                        else:
                            if part.strip():
                                add_paragraph(doc, part.strip())
                else:
                    add_paragraph(doc, value)
            elif isinstance(value, dict):
                # 递归处理子内容
                process_chapter_content(doc, value, images_dir)

def generate_chapter(content, output_path, images_dir=None):
    """
    生成章节文档
    
    Args:
        content: 章节内容（JSON格式）
        output_path: 输出文件路径
        images_dir: 截图目录
    """
    doc = create_chapter_document()
    process_chapter_content(doc, content, images_dir)
    doc.save(output_path)
    print(f"章节文档已保存到：{output_path}")

def main():
    parser = argparse.ArgumentParser(description='生成说明书章节')
    parser.add_argument('--content', required=True, help='内容JSON文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--images-dir', help='截图目录路径')
    args = parser.parse_args()
    
    # 读取内容
    with open(args.content, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    # 生成章节
    generate_chapter(content, args.output, args.images_dir)

if __name__ == '__main__':
    main()
