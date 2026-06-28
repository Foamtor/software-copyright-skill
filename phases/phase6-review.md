# 阶段6：审阅提交

## 目标

检查文档完整性和内容质量，生成提交清单。

## 流程

### 1. 检查文档完整性

```bash
ls -la output/*.docx
```

确认三份文档都已生成：
- ✅ 信息采集表.docx
- ✅ 使用说明书.docx
- ✅ 源代码文档.docx

### 2. 检查格式规范

```bash
python3 scripts/validate_output.py --docx output/说明书.docx
```

检查项目：
- 字号是否正确（封面22pt，标题16pt，正文16pt，图名14pt）
- 字体是否正确（标题黑体，正文Times New Roman）
- 缩进是否正确（首行1.18cm）
- 行距是否正确（1.5倍）

### 3. ⚠️ 检查内容质量

```python
from docx import Document

def check_content_quality(docx_path):
    """检查内容质量"""
    doc = Document(docx_path)
    
    # 统计总字数
    total_chars = sum(len(p.text) for p in doc.paragraphs if p.text.strip())
    
    # 统计截图标记
    screenshot_count = sum(1 for p in doc.paragraphs if '[截图' in p.text or p.text.strip().startswith('图'))
    
    # 统计注意事项
    note_count = sum(1 for p in doc.paragraphs if '注意事项' in p.text)
    
    # 统计章节数
    chapter_count = sum(1 for p in doc.paragraphs if p.text.strip().startswith(('一、', '二、', '三、', '四、', '五、', '六、', '七、', '八、', '九、', '十、')))
    
    print(f"=== 内容质量检查 ===")
    print(f"总字数: {total_chars} (要求≥15000) {'✅' if total_chars >= 15000 else '❌'}")
    print(f"章节数: {chapter_count} (要求6-10章) {'✅' if 6 <= chapter_count <= 10 else '❌'}")
    print(f"截图标记: {screenshot_count} (要求≥50) {'✅' if screenshot_count >= 50 else '❌'}")
    print(f"注意事项: {note_count} (要求≥30) {'✅' if note_count >= 30 else '❌'}")
    
    return {
        "total_chars": total_chars,
        "chapter_count": chapter_count,
        "screenshot_count": screenshot_count,
        "note_count": note_count,
        "quality_pass": total_chars >= 15000 and 6 <= chapter_count <= 10 and screenshot_count >= 50 and note_count >= 30
    }

# 检查说明书
quality = check_content_quality('output/说明书.docx')

if not quality["quality_pass"]:
    print("\n⚠️ 内容质量不达标，需要补充内容")
    if quality["total_chars"] < 15000:
        print(f"   字数差距: {15000 - quality['total_chars']} 字")
    if quality["screenshot_count"] < 50:
        print(f"   截图差距: {50 - quality['screenshot_count']} 张")
    if quality["note_count"] < 30:
        print(f"   注意事项差距: {30 - quality['note_count']} 个")
```

### 4. 统计页数和字数

```python
from docx import Document

# 说明书
doc = Document('output/说明书.docx')
print(f"说明书：{len(doc.paragraphs)} 段落，{sum(len(p.text) for p in doc.paragraphs)} 字")

# 代码文档
doc = Document('output/代码文档.docx')
print(f"代码文档：{len(doc.paragraphs)} 段落")
```

### 5. 生成提交清单

```
软著申请提交清单

一、申请信息
- 软件名称：国农臻汇APPV1.0
- 版本号：V1.0
- 著作权人：农业农村部乡村振兴监测中心
- 完成日期：2026年6月

二、提交材料
1. 信息采集表（1份）
2. 使用说明书（XX页，XX字）
3. 源代码文档（60页）

三、内容质量指标
- 说明书总字数：XX字（要求≥15000）✅/❌
- 截图标记数量：XX张（要求≥50）✅/❌
- 注意事项数量：XX个（要求≥30）✅/❌

四、提交步骤
1. 登录中国版权保护中心网站
2. 填写在线申请表
3. 上传材料
4. 提交审核

五、注意事项
1. 所有材料必须是.docx格式
2. 说明书不少于10页
3. 代码文档前30页+后30页
4. 截图需要手动补充
```

### 6. 最终确认

展示所有文档：
```
所有文档已生成，请最终审阅：

1. 信息采集表：output/信息采集表.docx
2. 使用说明书：output/说明书.docx（共XX页，XX字）
3. 代码文档：output/代码文档.docx（共60页）

内容质量指标：
- 总字数：XX字 ✅/❌
- 截图标记：XX张 ✅/❌
- 注意事项：XX个 ✅/❌

请确认是否有需要修改的地方。
```

## 输出

- `output/提交清单.md` — 提交清单
- 三份Word文档

## 内容质量标准

| 指标 | 标准 | 检查方法 |
|------|------|----------|
| **总字数** | ≥15000字 | `sum(len(p.text) for p in doc.paragraphs)` |
| **章节数** | 6-10章 | 按功能模块组织 |
| **截图标记** | ≥50张 | `count([截图: xxx])` |
| **注意事项** | ≥30个 | `count(注意事项)` |
| **每章字数** | ≥1500字 | 详细描述操作步骤 |
| **每节字数** | ≥300字 | 包含完整操作流程 |

## 注意事项

1. **检查完整性** — 三份文档缺一不可
2. **检查格式** — 字号、字体、缩进、行距
3. **⚠️ 检查内容质量** — 字数、截图、注意事项必须达标
4. **统计页数** — 说明书不少于10页，代码文档60页
5. **截图补充** — 说明书中图片标题是占位符，需手动补充
6. **用户确认** — 最终由用户确认后提交
