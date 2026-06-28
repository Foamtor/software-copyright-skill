# 阶段5：文档生成

## 目标

使用脚本生成三份Word文档，并验证内容质量和格式。

## 流程

### 1. 生成说明书

```bash
python3 scripts/generate_manual.py \
  --content output/content.json \
  --template templates/manual_template.docx \
  --output output/说明书.docx
```

### 2. 生成代码文档

```bash
python3 scripts/generate_code_doc.py \
  --project /path/to/project \
  --files output/file_list.json \
  --output output/代码文档.docx \
  --software-name "软件名称" \
  --version "V1.0"
```

**代码提取规则**：
- 每页≥50行，前30页+后30页，共60页
- 按65页计算（考虑封面页等额外页数）
- 提取顺序：主入口 → 路由 → 核心页面 → 公共组件 → API → 工具函数
- 排除第三方库：node_modules/、.venv/、__pycache__/、dist/

### 3. 生成信息采集表

```bash
python3 scripts/fill_template.py \
  --info output/info.json \
  --template templates/info_template.docx \
  --output output/信息采集表.docx \
  --software-name "软件名称" \
  --version "V1.0"
```

### 4. 验证格式

```bash
python3 scripts/validate_output.py --docx output/说明书.docx
```

检查项目：
- 字号是否正确（封面22pt，标题16pt，正文16pt，图名14pt）
- 字体是否正确（标题黑体，正文Times New Roman）
- 缩进是否正确（首行1.18cm）
- 行距是否正确（1.5倍）

### 5. ⚠️ 验证内容质量

```bash
python3 << 'EOF'
from docx import Document

doc = Document('output/说明书.docx')

# 统计总字数
total_chars = sum(len(p.text) for p in doc.paragraphs if p.text.strip())

# 统计截图标记
screenshot_count = sum(1 for p in doc.paragraphs if '[截图' in p.text or p.text.strip().startswith('图'))

# 统计注意事项
note_count = sum(1 for p in doc.paragraphs if '注意事项' in p.text)

print(f"=== 内容质量检查 ===")
print(f"总字数: {total_chars} (要求≥15000) {'✅' if total_chars >= 15000 else '❌'}")
print(f"截图标记: {screenshot_count} (要求≥50) {'✅' if screenshot_count >= 50 else '❌'}")
print(f"注意事项: {note_count} (要求≥30) {'✅' if note_count >= 30 else '❌'}")

if total_chars < 15000:
    print(f"\n⚠️ 字数不足，需要补充内容")
    print(f"   差距: {15000 - total_chars} 字")
EOF
```

### 6. 配图处理

如果有Excalidraw生成的配图：
```bash
python3 scripts/replace_docx_images.py \
  --docx output/说明书.docx \
  --images-map output/images_map.json \
  --output output/说明书_含配图.docx
```

## 输出

- `output/说明书.docx` — 使用说明书
- `output/代码文档.docx` — 源代码文档
- `output/信息采集表.docx` — 信息采集表

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

1. **必须输出.docx** — 绝对不要输出.md文件
2. **模板是格式来源** — 格式由模板控制，不在JSON中
3. **代码文档按65页提取** — 考虑额外页数
4. **⚠️ 验证内容质量** — 字数、截图、注意事项必须达标
5. **验证输出** — 生成后检查页数、字数、格式
6. **配图可后续补充** — 图片标题是占位符，用户可手动补充
