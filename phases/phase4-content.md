# 阶段4：内容生成

## 目标

按章节分步生成JSON内容，确保内容质量达标后保存。

## ⚠️ 核心原则：模型生成 + 脚本验证

**本阶段的职责分工：**

| 步骤 | 执行者 | 说明 |
|------|--------|------|
| 生成章节内容 | 🤖 模型 | 使用 `prompts/章节生成.md` 指导模型 |
| 审阅章节质量 | 🤖 模型 | 使用 `prompts/章节审阅.md` 指导模型 |
| 基础质量检查 | 🐍 脚本 | 使用 `scripts/review_chapter.py` 检查字数、数量 |
| 内容质量验证 | 🐍 脚本 | 使用 `scripts/validate_content_quality.py` 验证整体质量 |
| 合并章节 | 🐍 脚本 | 使用 `scripts/merge_chapters.py` 合并为content.json |

## 分步生成流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 模型生成第1章                                             │
│    - 使用 prompts/章节生成.md 作为prompt模板                  │
│    - 输出符合格式的JSON数组                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 模型审阅第1章                                             │
│    - 使用 prompts/章节审阅.md 作为prompt模板                  │
│    - 检查写作风格、内容完整性、术语一致性                      │
│    - 输出审阅结果和修改建议                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 脚本检查第1章基础质量                                     │
│    - 使用 scripts/review_chapter.py                          │
│    - 检查：字数≥1500、notes≥3、images≥2                      │
│    - 输出检查结果                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 保存第1章到 chapter1.json                                 │
│    - 生成章节摘要供后续章节使用                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 重复步骤1-4，生成第2-N章                                   │
│    - 每章生成时传入前几章摘要                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. 合并所有章节                                              │
│    - 使用 scripts/merge_chapters.py                          │
│    - 生成 content.json                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. 脚本验证整体内容质量                                       │
│    - 使用 scripts/validate_content_quality.py                │
│    - 检查：总字数≥15000、截图≥50、注意事项≥30                 │
└─────────────────────────────────────────────────────────────┘
```

## 详细步骤

### 步骤1：模型生成章节内容

**执行者**：模型

**输入**：
- 项目信息（project_info）
- 本章大纲（chapter_outline）
- 前几章摘要（previous_summaries）
- 截图列表（screenshots）

**使用的prompt**：`prompts/章节生成.md`

**输出格式**：
```json
[
  {
    "heading": "（一）xxx功能",
    "content": "详细的操作描述...",
    "images": [
      {"ref": "图3", "description": "xxx按钮位置"},
      {"ref": "图4", "description": "xxx对话框"}
    ],
    "notes": [
      "注意事项1",
      "注意事项2",
      "注意事项3"
    ]
  }
]
```

### 步骤2：模型审阅章节内容

**执行者**：模型

**输入**：
- 章节内容（chapter_content）
- 大纲要求（chapter_outline）
- 前几章摘要（previous_summaries）
- 项目信息（project_info）

**使用的prompt**：`prompts/章节审阅.md`

**输出格式**：
```json
{
  "审阅结果": "通过/需修改",
  "问题列表": [...],
  "修改后内容": [...]
}
```

**处理逻辑**：
- 如果"审阅结果"为"通过"，继续步骤3
- 如果"审阅结果"为"需修改"，使用"修改后内容"替换原内容

### 步骤3：脚本检查基础质量

**执行者**：Python脚本

**使用的脚本**：`scripts/review_chapter.py`

**检查项目**：
- 每个section的content字数 ≥ 300
- 每个section的notes数量 ≥ 3
- 每个section的images数量 ≥ 2
- 整章字数 ≥ 1500

**⚠️ 第一章特殊处理**：
- 第一章"平台总体介绍"是介绍性内容，不适用"用户操作指南"风格检查
- 检查第一章时使用 `--is-chapter1` 参数跳过写作风格检查
- 命令：`python3 scripts/review_chapter.py --chapter chapter1.json --is-chapter1`

**输出**：
```
=== 第X章质量检查 ===
（一）xxx功能: content=523字 ✅, notes=4个 ✅, images=3张 ✅
（二）xxx功能: content=287字 ❌ (要求≥300), notes=2个 ❌ (要求≥3), images=2张 ✅

整章字数: 1523字 ✅ (要求≥1500)
```

### 步骤4：保存章节

**执行者**：Python脚本

**保存内容**：
- 章节JSON内容 → `output/chapters/chapter{N}.json`
- 进度记录 → `output/progress.json`

**进度记录格式**：
```json
{
  "total_chapters": 8,
  "completed_chapters": [1, 2, 3],
  "current_chapter": 4,
  "last_update": "2026-06-26T12:00:00"
}
```

### 步骤5：重复生成

**执行者**：模型 + 脚本

**上下文传递**：
- 每章生成时，传入前几章的摘要
- 摘要包含：章节标题、主要内容、截图数量

### 步骤6：合并章节

**执行者**：Python脚本

**使用的脚本**：`scripts/merge_chapters.py`

**输入**：`output/chapters/chapter*.json`

**输出**：`output/content.json`

### 步骤7：验证整体质量

**执行者**：Python脚本

**使用的脚本**：`scripts/validate_content_quality.py`

**检查项目**：
- 总字数 ≥ 15000
- 章节数 6-10章
- 截图标记 ≥ 50
- 注意事项 ≥ 30

**输出**：
```
=== 内容质量验证 ===
总字数: 18234 ✅ (要求≥15000)
章节数: 8 ✅ (要求6-10章)
截图标记: 62 ✅ (要求≥50)
注意事项: 35 ✅ (要求≥30)

✅ 内容质量验证通过
```

## 断点续传

中断后继续：

```python
def resume_generation():
    """断点续传"""
    progress = load_progress()
    
    # 从上次中断的位置继续
    for chapter_id in range(progress["current_chapter"], progress["total_chapters"] + 1):
        # 加载前几章摘要
        previous_summaries = load_summaries(progress["completed_chapters"])
        
        # 生成当前章节（模型）
        chapter_content = generate_chapter(chapter_id, chapters[chapter_id], previous_summaries)
        
        # 审阅当前章节（模型）
        review_result = review_chapter(chapter_content, chapters[chapter_id])
        if review_result["审阅结果"] == "需修改":
            chapter_content = review_result["修改后内容"]
        
        # 检查基础质量（脚本）
        check_result = check_chapter_quality(chapter_content)
        if not check_result["passed"]:
            print(f"⚠️ 第{chapter_id}章质量检查未通过：{check_result['issues']}")
        
        # 保存章节
        save_chapter(chapter_id, chapter_content)
        
        # 更新进度
        progress["completed_chapters"].append(chapter_id)
        progress["current_chapter"] = chapter_id + 1
        save_progress(progress)
```

## 关键设计

1. **模型负责生成和审阅**：内容生成、风格判断、质量审阅由模型完成
2. **脚本负责验证和控制**：字数统计、数量检查、流程控制由脚本完成
3. **分步生成**：避免模型一次性输出所有内容导致长度不足
4. **上下文传递**：每章生成时传入前几章摘要，保持内容一致性
5. **断点续传**：每章保存到独立文件，中断后可从上次位置继续
