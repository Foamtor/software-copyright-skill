#!/usr/bin/env python3
"""
软著文档内容质量验证脚本。

用法：
  python3 validate_content_quality.py --content content.json
  python3 validate_content_quality.py --chapters output/chapters/

功能：
  1. 统计总字数、章节数、截图标记、注意事项数量
  2. 检查每章字数、每节字数、notes数量、images数量
  3. 输出验证结果
"""

import argparse
import json
import os
from pathlib import Path


def count_chars(text):
    """统计字数（不含空格和换行）"""
    return len(text.replace(" ", "").replace("\n", ""))


def validate_section(section, section_index):
    """验证单个section的质量"""
    issues = []
    
    content = section.get("content", "")
    notes = section.get("notes", [])
    images = section.get("images", [])
    heading = section.get("heading", f"section_{section_index}")
    
    content_chars = count_chars(content)
    notes_count = len(notes)
    images_count = len(images)
    
    if content_chars < 300:
        issues.append(f"content字数不足: {content_chars}字 (要求≥300)")
    
    # 精简版：notes不再强制要求
    # if notes_count < 3:
    #     issues.append(f"notes数量不足: {notes_count}个 (要求≥3)")
    
    # 精简版：每节≥1张图片即可
    if images_count < 1:
        issues.append(f"images数量不足: {images_count}张 (要求≥1)")
    
    return {
        "heading": heading,
        "content_chars": content_chars,
        "notes_count": notes_count,
        "images_count": images_count,
        "passed": len(issues) == 0,
        "issues": issues
    }


def validate_chapter(chapter, chapter_index):
    """验证单个章节的质量"""
    issues = []
    section_results = []
    
    # 支持两种结构：
    # 1. chapter.sections = [...]
    # 2. chapter.subsections = [...] (当前结构)
    sections = chapter.get("sections", []) or chapter.get("subsections", [])
    if not sections:
        # 如果chapter没有sections/subsections字段，则将chapter本身视为一个section
        sections = [chapter]
    
    total_chars = 0
    for i, section in enumerate(sections):
        result = validate_section(section, i)
        section_results.append(result)
        total_chars += result["content_chars"]
        
        if not result["passed"]:
            issues.extend([f"{result['heading']}: {issue}" for issue in result["issues"]])
    
    if total_chars < 1500:
        issues.append(f"整章字数不足: {total_chars}字 (要求≥1500)")
    
    return {
        "chapter_index": chapter_index,
        "section_count": len(sections),
        "total_chars": total_chars,
        "section_results": section_results,
        "passed": len(issues) == 0,
        "issues": issues
    }


def validate_content(content_data):
    """验证整个content的质量"""
    issues = []
    chapter_results = []
    
    # 统计总量
    total_chars = 0
    total_sections = 0
    total_notes = 0
    total_images = 0
    total_chapters = 0
    
    # 获取章节列表
    chapters = content_data.get("chapters", [])
    
    # 如果没有chapters字段，将sections视为章节
    if not chapters:
        sections = content_data.get("sections", [])
        # 检查sections是否有subsections
        if sections and "subsections" in sections[0]:
            # sections是章节列表，每个章节有subsections
            chapters = sections
        else:
            # sections是section列表，视为单个章节
            chapters = [{"sections": sections}]
    
    # 验证每个章节
    for i, chapter in enumerate(chapters):
        result = validate_chapter(chapter, i)
        chapter_results.append(result)
        
        total_chars += result["total_chars"]
        total_sections += result["section_count"]
        
        for section_result in result["section_results"]:
            total_notes += section_result["notes_count"]
            total_images += section_result["images_count"]
        
        if not result["passed"]:
            issues.extend(result["issues"])
    
    total_chapters = len(chapters)
    
    # 检查总体指标（精简版标准）
    if total_chars < 15000:
        issues.append(f"总字数不足: {total_chars}字 (要求≥15000)")
    
    if total_chapters < 6 or total_chapters > 10:
        issues.append(f"章节数不符合要求: {total_chapters}章 (要求6-10章)")
    
    # 精简版配图标准：13-16张
    if total_images < 13:
        issues.append(f"截图标记不足: {total_images}张 (要求≥13)")
    
    # 注意事项已取消强制要求
    # if total_notes < 30:
    #     issues.append(f"注意事项不足: {total_notes}个 (要求≥30)")
    
    return {
        "total_chars": total_chars,
        "total_chapters": total_chapters,
        "total_sections": total_sections,
        "total_notes": total_notes,
        "total_images": total_images,
        "chapter_results": chapter_results,
        "passed": len(issues) == 0,
        "issues": issues
    }


def print_report(result):
    """打印验证报告"""
    print("=== 内容质量验证报告 ===\n")
    
    # 总体指标
    print("【总体指标】")
    print(f"  总字数: {result['total_chars']}字 {'✅' if result['total_chars'] >= 15000 else '❌'} (要求≥15000)")
    print(f"  章节数: {result['total_chapters']}章 {'✅' if 6 <= result['total_chapters'] <= 10 else '❌'} (要求6-10章)")
    print(f"  截图标记: {result['total_images']}张 {'✅' if result['total_images'] >= 50 else '❌'} (要求≥50)")
    print(f"  注意事项: {result['total_notes']}个 {'✅' if result['total_notes'] >= 30 else '❌'} (要求≥30)")
    print()
    
    # 每章详情
    print("【每章详情】")
    for chapter_result in result['chapter_results']:
        status = "✅" if chapter_result['passed'] else "❌"
        print(f"  第{chapter_result['chapter_index']+1}章: {chapter_result['total_chars']}字, {chapter_result['section_count']}节 {status}")
        
        for section_result in chapter_result['section_results']:
            status = "✅" if section_result['passed'] else "❌"
            print(f"    - {section_result['heading']}: content={section_result['content_chars']}字, notes={section_result['notes_count']}个, images={section_result['images_count']}张 {status}")
            
            if section_result['issues']:
                for issue in section_result['issues']:
                    print(f"      ⚠️ {issue}")
    
    print()
    
    # 问题汇总
    if result['issues']:
        print("【问题汇总】")
        for issue in result['issues']:
            print(f"  ❌ {issue}")
        print()
        print("❌ 内容质量验证未通过")
    else:
        print("✅ 内容质量验证通过")


def main():
    parser = argparse.ArgumentParser(description="软著文档内容质量验证")
    parser.add_argument("--content", help="content.json文件路径")
    parser.add_argument("--chapters", help="章节目录路径")
    parser.add_argument("--json", action="store_true", help="输出JSON格式结果")
    
    args = parser.parse_args()
    
    if not args.content and not args.chapters:
        parser.error("必须指定 --content 或 --chapters")
    
    content_data = {}
    
    if args.content:
        with open(args.content, 'r', encoding='utf-8') as f:
            content_data = json.load(f)
    
    elif args.chapters:
        chapters_dir = Path(args.chapters)
        if not chapters_dir.exists():
            print(f"❌ 章节目录不存在: {args.chapters}")
            return
        
        chapters = []
        for chapter_file in sorted(chapters_dir.glob("chapter*.json")):
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
                # 每个chapter文件视为一个chapter
                chapters.append({"sections": chapter_data if isinstance(chapter_data, list) else [chapter_data]})
        
        content_data = {"chapters": chapters}
    
    result = validate_content(content_data)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)
    
    return 0 if result['passed'] else 1


if __name__ == "__main__":
    exit(main())
