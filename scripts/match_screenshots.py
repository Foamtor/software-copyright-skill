     1|#!/usr/bin/env python3
     2|"""
     3|智能匹配截图脚本
     4|根据说明书功能描述，自动匹配用户提供的截图
     5|
     6|使用方式：
     7|1. 扫描截图文件夹，获取所有图片
     8|2. 用视觉模型分析每张截图内容
     9|3. 根据功能描述匹配最合适的截图
    10|4. 输出匹配结果供用户确认
    11|
    12|依赖：
    13|- 需要视觉模型支持（如Claude Vision、GPT-4V等）
    14|- Pillow (图片处理)
    15|"""
    16|
    17|import os
    18|import json
    19|import argparse
    20|from pathlib import Path
    21|from typing import Dict, List, Optional
    22|
    23|# 支持的图片格式
    24|IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'}
    25|
    26|
    27|def scan_screenshots_folder(folder_path: str) -> List[Dict]:
    28|    """
    29|    扫描截图文件夹，获取所有图片文件
    30|    
    31|    Args:
    32|        folder_path: 截图文件夹路径
    33|        
    34|    Returns:
    35|        图片文件列表 [{"path": str, "name": str, "size": int}]
    36|    """
    37|    screenshots = []
    38|    folder = Path(folder_path)
    39|    
    40|    if not folder.exists():
    41|        print(f"错误：文件夹不存在 {folder_path}")
    42|        return screenshots
    43|    
    44|    for file_path in sorted(folder.iterdir()):
    45|        if file_path.suffix.lower() in IMAGE_EXTENSIONS:
    46|            screenshots.append({
    47|                "path": str(file_path),
    48|                "name": file_path.name,
    49|                "size": file_path.stat().st_size,
    50|                "stem": file_path.stem  # 不含扩展名的文件名
    51|            })
    52|    
    53|    print(f"找到 {len(screenshots)} 张截图")
    54|    return screenshots
    55|
    56|
    57|def analyze_screenshot(image_path: str) -> Dict:
    58|    """
    59|    用视觉模型分析截图内容
    60|    
    61|    Args:
    62|        image_path: 图片路径
    63|        
    64|    Returns:
    65|        分析结果 {"page_title": str, "elements": list, "description": str}
    66|    """
    67|    # 注意：这个函数需要在Hermes Agent环境中调用
    68|    # 实际实现时会调用 vision_analyze 工具
    69|    
    70|    analysis_prompt = """请分析这张系统截图，识别以下信息：
    71|1. 页面标题（如果有）
    72|2. 主要功能区域（导航栏、表单、表格、按钮等）
    73|3. 页面类型（登录页、列表页、详情页、表单页、仪表盘等）
    74|4. 关键功能描述（这个页面主要做什么）
    75|
    76|请用JSON格式返回：
    77|{
    78|    "page_title": "页面标题",
    79|    "page_type": "页面类型",
    80|    "elements": ["元素1", "元素2", ...],
    81|    "description": "功能描述",
    82|    "keywords": ["关键词1", "关键词2", ...]
    83|}"""
    84|    
    85|    # 这里是占位符，实际实现时需要调用 vision_analyze
    86|    # 在 Hermes Agent 环境中，会通过 tool 调用实现
    87|    return {
    88|        "page_title": "",
    89|        "page_type": "",
    90|        "elements": [],
    91|        "description": "",
    92|        "keywords": [],
    93|        "image_path": image_path,
    94|        "needs_analysis": True  # 标记需要视觉分析
    95|    }
    96|
    97|
    98|def match_screenshot_to_chapter(
    99|    screenshot_analysis: Dict,
   100|    chapter_info: Dict
   101|) -> float:
   102|    """
   103|    计算截图与章节的匹配度
   104|    
   105|    Args:
   106|        screenshot_analysis: 截图分析结果
   107|        chapter_info: 章节信息 {"title": str, "description": str, "keywords": list}
   108|        
   109|    Returns:
   110|        匹配度分数 (0-1)
   111|    """
   112|    score = 0.0
   113|    
   114|    # 提取关键词
   115|    screenshot_keywords = set(screenshot_analysis.get("keywords", []))
   116|    chapter_keywords = set(chapter_info.get("keywords", []))
   117|    
   118|    # 页面标题匹配
   119|    if screenshot_analysis.get("page_title"):
   120|        chapter_title = chapter_info.get("title", "")
   121|        if screenshot_analysis["page_title"] in chapter_title:
   122|            score += 0.4
   123|        elif any(kw in chapter_title for kw in screenshot_keywords):
   124|            score += 0.2
   125|    
   126|    # 关键词匹配
   127|    if screenshot_keywords and chapter_keywords:
   128|        overlap = screenshot_keywords & chapter_keywords
   129|        if overlap:
   130|            score += 0.3 * (len(overlap) / max(len(screenshot_keywords), len(chapter_keywords)))
   131|    
   132|    # 页面类型匹配
   133|    page_type = screenshot_analysis.get("page_type", "")
   134|    chapter_desc = chapter_info.get("description", "")
   135|    type_mapping = {
   136|        "登录页": ["登录", "登陆", "认证", "账号"],
   137|        "列表页": ["列表", "查询", "搜索", "浏览"],
   138|        "详情页": ["详情", "查看", "信息", "资料"],
   139|        "表单页": ["新建", "编辑", "添加", "修改", "录入"],
   140|        "仪表盘": ["首页", "概览", "统计", "总览", "主页"]
   141|    }
   142|    
   143|    if page_type in type_mapping:
   144|        if any(kw in chapter_desc for kw in type_mapping[page_type]):
   145|            score += 0.3
   146|    
   147|    return min(score, 1.0)
   148|
   149|
   150|def match_screenshots_to_manual(
   151|    screenshots: List[Dict],
   152|    manual_content: Dict
   153|) -> List[Dict]:
   154|    """
   155|    将截图匹配到说明书章节
   156|    
   157|    Args:
   158|        screenshots: 截图列表（含分析结果）
   159|        manual_content: 说明书内容JSON
   160|        
   161|    Returns:
   162|        匹配结果列表
   163|    """
   164|    # 提取所有需要截图的章节
   165|    chapters = extract_chapters_with_screenshots(manual_content)
   166|    
   167|    # 为每个截图找到最佳匹配章节
   168|    matches = []
   169|    used_chapters = set()
   170|    
   171|    for screenshot in screenshots:
   172|        if not screenshot.get("analysis"):
   173|            continue
   174|        
   175|        best_match = None
   176|        best_score = 0.0
   177|        
   178|        for i, chapter in enumerate(chapters):
   179|            if i in used_chapters:
   180|                continue
   181|            
   182|            score = match_screenshot_to_chapter(
   183|                screenshot["analysis"],
   184|                chapter
   185|            )
   186|            
   187|            if score > best_score:
   188|                best_score = score
   189|                best_match = {
   190|                    "chapter_index": i,
   191|                    "chapter": chapter,
   192|                    "score": score
   193|                }
   194|        
   195|        if best_match and best_match["score"] > 0.3:  # 匹配阈值
   196|            used_chapters.add(best_match["chapter_index"])
   197|            matches.append({
   198|                "screenshot": screenshot,
   199|                "chapter": best_match["chapter"],
   200|                "score": best_match["score"],
   201|                "confidence": "high" if best_match["score"] > 0.7 else "medium"
   202|            })
   203|    
   204|    # 按章节顺序排序
   205|    matches.sort(key=lambda x: x["chapter"].get("order", 0))
   206|    
   207|    return matches
   208|
   209|
   210|def extract_chapters_with_screenshots(manual_content: Dict) -> List[Dict]:
   211|    """
   212|    从说明书内容中提取需要截图的章节
   213|    
   214|    Args:
   215|        manual_content: 说明书内容JSON
   216|        
   217|    Returns:
   218|        章节信息列表
   219|    """
   220|    chapters = []
   221|    
   222|    def extract_from_dict(content, path="", order=0):
   223|        for key, value in content.items():
   224|            current_path = f"{path}/{key}" if path else key
   225|            
   226|            if isinstance(value, str):
   227|                # 检查是否包含截图占位符
   228|                if "[截图:" in value or "如下图" in value:
   229|                    # 提取关键词
   230|                    keywords = extract_keywords_from_text(value)
   231|                    chapters.append({
   232|                        "path": current_path,
   233|                        "title": key,
   234|                        "description": value,
   235|                        "keywords": keywords,
   236|                        "order": order
   237|                    })
   238|                    order += 1
   239|            elif isinstance(value, dict):
   240|                order = extract_from_dict(value, current_path, order)
   241|            elif isinstance(value, list):
   242|                for i, item in enumerate(value):
   243|                    if isinstance(item, dict):
   244|                        order = extract_from_dict(item, f"{current_path}[{i}]", order)
   245|        
   246|        return order
   247|    
   248|    extract_from_dict(manual_content)
   249|    return chapters
   250|
   251|
   252|def extract_keywords_from_text(text: str) -> List[str]:
   253|    """
   254|    从文本中提取关键词
   255|    
   256|    Args:
   257|        text: 文本内容
   258|        
   259|    Returns:
   260|        关键词列表
   261|    """
   262|    # 简单的关键词提取（实际实现可以用jieba分词）
   263|    keywords = []
   264|    
   265|    # 常见功能关键词
   266|    feature_keywords = [
   267|        "登录", "注册", "查询", "搜索", "新建", "编辑", "删除",
   268|        "导入", "导出", "上传", "下载", "列表", "详情", "统计",
   269|        "首页", "设置", "管理", "审核", "审批", "提交", "保存"
   270|    ]
   271|    
   272|    for kw in feature_keywords:
   273|        if kw in text:
   274|            keywords.append(kw)
   275|    
   276|    return keywords
   277|
   278|
   279|def generate_match_report(matches: List[Dict], output_path: str):
   280|    """
   281|    生成匹配报告
   282|    
   283|    Args:
   284|        matches: 匹配结果列表
   285|        output_path: 输出路径
   286|    """
   287|    report = {
   288|        "total_matches": len(matches),
   289|        "matches": []
   290|    }
   291|    
   292|    for match in matches:
   293|        report["matches"].append({
   294|            "screenshot": match["screenshot"]["name"],
   295|            "chapter": match["chapter"]["title"],
   296|            "chapter_path": match["chapter"]["path"],
   297|            "score": match["score"],
   298|            "confidence": match["confidence"],
   299|            "suggestion": f"建议将 {match['screenshot']['name']} 插入到 {match['chapter']['title']}"
   300|        })
   301|    
   302|    # 保存JSON报告
   303|    with open(output_path, 'w', encoding='utf-8') as f:
   304|        json.dump(report, f, ensure_ascii=False, indent=2)
   305|    
   306|    # 生成可读报告
   307|    readable_path = output_path.replace('.json', '_可读.md')
   308|    with open(readable_path, 'w', encoding='utf-8') as f:
   309|        f.write("# 截图匹配报告\n\n")
   310|        f.write(f"共匹配 {len(matches)} 张截图\n\n")
   311|        
   312|        for i, match in enumerate(matches, 1):
   313|            f.write(f"## 匹配 {i}\n\n")
   314|            f.write(f"- **截图**: {match['screenshot']['name']}\n")
   315|            f.write(f"- **目标章节**: {match['chapter']['title']}\n")
   316|            f.write(f"- **章节路径**: {match['chapter']['path']}\n")
   317|            f.write(f"- **匹配度**: {match['score']:.2f}\n")
   318|            f.write(f"- **置信度**: {match['confidence']}\n\n")
   319|    
   320|    print(f"匹配报告已保存到：{output_path}")
   321|    print(f"可读报告已保存到：{readable_path}")
   322|
   323|
   324|def main():
   325|    parser = argparse.ArgumentParser(description='智能匹配截图到说明书章节')
   326|    parser.add_argument('--screenshots', required=True, help='截图文件夹路径')
   327|    parser.add_argument('--manual', required=True, help='说明书内容JSON文件')
   328|    parser.add_argument('--output', required=True, help='输出报告路径')
   329|    parser.add_argument('--threshold', type=float, default=0.3, help='匹配阈值 (0-1)')
   330|    args = parser.parse_args()
   331|    
   332|    # 1. 扫描截图文件夹
   333|    screenshots = scan_screenshots_folder(args.screenshots)
   334|    if not screenshots:
   335|        print("错误：没有找到截图文件")
   336|        return
   337|    
   338|    # 2. 读取说明书内容
   339|    with open(args.manual, 'r', encoding='utf-8') as f:
   340|        manual_content = json.load(f)
   341|    
   342|    # 3. 分析截图（需要视觉模型支持）
   343|    print("注意：截图分析需要视觉模型支持")
   344|    print("请在 Hermes Agent 环境中运行，或手动提供截图分析结果")
   345|    
   346|    # 4. 匹配截图到章节
   347|    matches = match_screenshots_to_manual(screenshots, manual_content)
   348|    
   349|    # 5. 生成报告
   350|    generate_match_report(matches, args.output)
   351|
   352|
   353|if __name__ == '__main__':
   354|    main()
   355|