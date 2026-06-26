#!/usr/bin/env python3
"""
软著文档单章质量检查脚本。

用法：
  python3 review_chapter.py --chapter chapter1.json
  python3 review_chapter.py --chapter chapter1.json --is-chapter1
  python3 review_chapter.py --chapter chapter1.json --json

功能：
  1. 检查每个section的content字数 ≥ 300
  2. 检查每个section的notes数量 ≥ 3
  3. 检查每个section的images数量 ≥ 2
  4. 检查整章字数 ≥ 1500
  5. 检查写作风格（第一章跳过风格检查）
"""

import argparse
import json
from pathlib import Path


def count_chars(text):
    """统计字数（不含空格和换行）"""
    return len(text.replace(" ", "").replace("\n", ""))


def check_write_style(content):
    """检查写作风格是否符合用户操作指南要求"""
    issues = []
    
    # 检查是否包含操作关键词
    action_keywords = ["点击", "输入", "选择", "查看", "填写", "提交", "确认", "打开", "进入"]
    has_action = any(keyword in content for keyword in action_keywords)
    
    # 检查是否包含"如下图"
    has_figure_ref = "如下图" in content
    
    # 检查是否包含"图X"标记
    has_figure_mark = "图" in content and any(c.isdigit() for c in content[content.find("图"):content.find("图")+5])
    
    # 检查是否有技术文档风格的错误写法
    tech_patterns = ["支持", "提供", "实现", "具备", "具有"]
    has_tech_style = any(pattern in content for pattern in tech_patterns)
    
    if not has_action:
        issues.append("缺少操作关键词（点击、输入、选择等）")
    
    if not has_figure_ref:
        issues.append("缺少'如下图'引用")
    
    if has_tech_style:
        issues.append("可能包含技术文档风格描述（支持、提供、实现等）")
    
    return {
        "has_action": has_action,
        "has_figure_ref": has_figure_ref,
        "has_figure_mark": has_figure_mark,
        "has_tech_style": has_tech_style,
        "passed": len(issues) == 0,
        "issues": issues
    }


def review_section(section, section_index, skip_style_check=False):
    """检查单个section的质量"""
    issues = []
    
    content = section.get("content", "")
    notes = section.get("notes", [])
    images = section.get("images", [])
    heading = section.get("heading", f"section_{section_index}")
    
    content_chars = count_chars(content)
    notes_count = len(notes)
    images_count = len(images)
    
    # 基础数量检查
    if content_chars < 300:
        issues.append(f"content字数不足: {content_chars}字 (要求≥300)")
    
    if notes_count < 3:
        issues.append(f"notes数量不足: {notes_count}个 (要求≥3)")
    
    if images_count < 2:
        issues.append(f"images数量不足: {images_count}张 (要求≥2)")
    
    # 写作风格检查（第一章跳过）
    style_result = {"passed": True, "issues": [], "skipped": skip_style_check}
    if not skip_style_check:
        style_result = check_write_style(content)
        if not style_result["passed"]:
            issues.extend(style_result["issues"])
    
    return {
        "heading": heading,
        "content_chars": content_chars,
        "notes_count": notes_count,
        "images_count": images_count,
        "style_check": style_result,
        "passed": len(issues) == 0,
        "issues": issues
    }


def review_chapter(chapter_data, is_chapter1=False):
    """检查整个章节的质量"""
    issues = []
    section_results = []
    
    sections = chapter_data if isinstance(chapter_data, list) else chapter_data.get("sections", [chapter_data])
    
    total_chars = 0
    for i, section in enumerate(sections):
        result = review_section(section, i, skip_style_check=is_chapter1)
        section_results.append(result)
        total_chars += result["content_chars"]
        
        if not result["passed"]:
            issues.extend([f"{result['heading']}: {issue}" for issue in result["issues"]])
    
    if total_chars < 1500:
        issues.append(f"整章字数不足: {total_chars}字 (要求≥1500)")
    
    return {
        "section_count": len(sections),
        "total_chars": total_chars,
        "is_chapter1": is_chapter1,
        "section_results": section_results,
        "passed": len(issues) == 0,
        "issues": issues
    }


def print_report(result):
    """打印检查报告"""
    print("=== 单章质量检查报告 ===\n")
    
    chapter_type = "（第一章-平台总体介绍）" if result.get("is_chapter1") else ""
    print(f"章节数: {result['section_count']}节 {chapter_type}")
    print(f"总字数: {result['total_chars']}字 {'✅' if result['total_chars'] >= 1500 else '❌'} (要求≥1500)")
    print()
    
    print("【各节详情】")
    for section_result in result['section_results']:
        status = "✅" if section_result['passed'] else "❌"
        print(f"  {section_result['heading']}:")
        print(f"    content: {section_result['content_chars']}字 {'✅' if section_result['content_chars'] >= 300 else '❌'}")
        print(f"    notes: {section_result['notes_count']}个 {'✅' if section_result['notes_count'] >= 3 else '❌'}")
        print(f"    images: {section_result['images_count']}张 {'✅' if section_result['images_count'] >= 2 else '❌'}")
        
        style = section_result['style_check']
        if style.get('skipped'):
            print(f"    写作风格: ⏭️ 跳过（第一章介绍性内容）")
        else:
            print(f"    写作风格: {'✅' if style['passed'] else '❌'}")
        
        if section_result['issues']:
            print(f"    ⚠️ 问题:")
            for issue in section_result['issues']:
                print(f"      - {issue}")
    
    print()
    
    if result['issues']:
        print("【问题汇总】")
        for issue in result['issues']:
            print(f"  ❌ {issue}")
        print()
        print("❌ 单章质量检查未通过")
    else:
        print("✅ 单章质量检查通过")


def main():
    parser = argparse.ArgumentParser(description="软著文档单章质量检查")
    parser.add_argument("--chapter", required=True, help="章节JSON文件路径")
    parser.add_argument("--is-chapter1", action="store_true", help="第一章标志（跳过写作风格检查）")
    parser.add_argument("--json", action="store_true", help="输出JSON格式结果")
    
    args = parser.parse_args()
    
    with open(args.chapter, 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    result = review_chapter(chapter_data, is_chapter1=args.is_chapter1)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)
    
    return 0 if result['passed'] else 1


if __name__ == "__main__":
    exit(main())
