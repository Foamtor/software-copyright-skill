#!/usr/bin/env python3
"""
内容质量迭代优化脚本

功能：
1. 验证内容质量
2. 根据验证报告生成修改建议
3. 支持多轮迭代直到验证通过

用法：
  python3 iterate_content.py --content content.json [--max-iterations 5]
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils import load_content, count_chars


def validate_content_quality(content):
    """验证内容质量，返回问题列表"""
    issues = []
    
    # 统计总体指标
    total_chars = 0
    total_images = 0
    total_chapters = 0
    
    for section in content.get('sections', []):
        total_chapters += 1
        
        # 检查subsections
        subsections = section.get('subsections', [])
        if not subsections:
            subsections = [section]
        
        chapter_chars = 0
        for sub in subsections:
            sub_chars = count_chars(sub.get('content', ''))
            sub_images = len(sub.get('images', []))
            
            total_chars += sub_chars
            total_images += sub_images
            chapter_chars += sub_chars
            
            # 检查每节字数
            if sub_chars < 300:
                issues.append({
                    'type': 'section_chars',
                    'heading': sub.get('heading', ''),
                    'actual': sub_chars,
                    'required': 300,
                    'suggestion': f"补充{300 - sub_chars}字详细描述"
                })
            
            # 检查每节配图
            if sub_images < 1:
                issues.append({
                    'type': 'section_images',
                    'heading': sub.get('heading', ''),
                    'actual': sub_images,
                    'required': 1,
                    'suggestion': "添加1张图片标记"
                })
        
        # 检查每章字数
        if chapter_chars < 1500:
            issues.append({
                'type': 'chapter_chars',
                'heading': section.get('heading', ''),
                'actual': chapter_chars,
                'required': 1500,
                'suggestion': f"补充{1500 - chapter_chars}字详细描述"
            })
    
    # 检查总体指标
    if total_chars < 15000:
        issues.append({
            'type': 'total_chars',
            'actual': total_chars,
            'required': 15000,
            'suggestion': f"总字数不足，需要补充{15000 - total_chars}字"
        })
    
    if total_chapters < 6 or total_chapters > 10:
        issues.append({
            'type': 'chapter_count',
            'actual': total_chapters,
            'required': '6-10',
            'suggestion': "章节数不符合要求"
        })
    
    if total_images < 13:
        issues.append({
            'type': 'total_images',
            'actual': total_images,
            'required': 13,
            'suggestion': f"配图不足，需要补充{13 - total_images}张"
        })
    
    return {
        'passed': len(issues) == 0,
        'total_chars': total_chars,
        'total_chapters': total_chapters,
        'total_images': total_images,
        'issues': issues
    }


def generate_modification_suggestions(validation_result):
    """根据验证结果生成修改建议"""
    suggestions = []
    
    for issue in validation_result['issues']:
        if issue['type'] == 'section_chars':
            suggestions.append({
                'action': 'expand',
                'target': issue['heading'],
                'amount': issue['required'] - issue['actual'],
                'instruction': f"在{issue['heading']}中补充{issue['required'] - issue['actual']}字，详细描述操作步骤"
            })
        
        elif issue['type'] == 'section_images':
            suggestions.append({
                'action': 'add_image',
                'target': issue['heading'],
                'instruction': f"在{issue['heading']}中添加图片标记，格式：'如下图。\\n图X 描述'"
            })
        
        elif issue['type'] == 'chapter_chars':
            suggestions.append({
                'action': 'expand_chapter',
                'target': issue['heading'],
                'amount': issue['required'] - issue['actual'],
                'instruction': f"在{issue['heading']}章节中补充{issue['required'] - issue['actual']}字"
            })
    
    return suggestions


def print_validation_report(validation_result):
    """打印验证报告"""
    print("=" * 60)
    print("内容质量验证报告")
    print("=" * 60)
    
    print(f"\n【总体指标】")
    print(f"  总字数: {validation_result['total_chars']}字 {'✅' if validation_result['total_chars'] >= 15000 else '❌'} (要求≥15000)")
    print(f"  章节数: {validation_result['total_chapters']}章 {'✅' if 6 <= validation_result['total_chapters'] <= 10 else '❌'} (要求6-10)")
    print(f"  配图数量: {validation_result['total_images']}张 {'✅' if validation_result['total_images'] >= 13 else '❌'} (要求≥13)")
    
    if validation_result['issues']:
        print(f"\n【问题列表】（共{len(validation_result['issues'])}个）")
        for i, issue in enumerate(validation_result['issues'], 1):
            heading = issue.get('heading', '总体')
            print(f"  {i}. {heading}: {issue['suggestion']}")
    
    print(f"\n{'✅ 验证通过' if validation_result['passed'] else '❌ 验证未通过，需要修改'}")


def print_modification_suggestions(suggestions):
    """打印修改建议"""
    print("\n" + "=" * 60)
    print("修改建议")
    print("=" * 60)
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. [{suggestion['action']}] {suggestion['target']}")
        print(f"   {suggestion['instruction']}")


def main():
    parser = argparse.ArgumentParser(description="内容质量迭代优化")
    parser.add_argument("--content", required=True, help="content.json文件路径")
    parser.add_argument("--max-iterations", type=int, default=5, help="最大迭代次数")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.content):
        print(f"❌ 文件不存在: {args.content}")
        exit(1)
    
    # 加载内容
    content = load_content(args.content)
    
    # 验证内容
    validation_result = validate_content_quality(content)
    
    if args.json:
        print(json.dumps(validation_result, ensure_ascii=False, indent=2))
    else:
        print_validation_report(validation_result)
        
        if not validation_result['passed']:
            suggestions = generate_modification_suggestions(validation_result)
            print_modification_suggestions(suggestions)
    
    # 返回状态码
    exit(0 if validation_result['passed'] else 1)


if __name__ == "__main__":
    main()
