# Word输出强制规则

## 背景

2026-06-23的软著任务中，Agent犯了严重错误：将所有文档内容写入Markdown文件，而不是使用Python脚本生成Word文档。用户指出"输出应该是word，为什么都变成了markdown"。

## 错误根因

1. Agent在execute_code中使用write_file直接输出.md文件
2. 没有调用skill中已有的Python脚本（generate_code_doc.py、fill_template.py等）
3. 违反了skill的核心原则："LLM是大脑，Python是手脚"

## 正确工作流

### 信息采集表
```bash
# 1. 创建内容JSON
# 2. 使用fill_template.py填充模板
python3 ~/.hermes/skills/productivity/ruanzhu-doc/scripts/fill_template.py \
  --template /path/to/template.docx \
  --content /path/to/content.json \
  --output 信息采集表.docx \
  --software-name "软件名称" \
  --version "V1.0"
```

### 源代码文档
```bash
# 1. 创建文件列表JSON
# 2. 使用generate_code_doc.py提取代码
python3 ~/.hermes/skills/productivity/ruanzhu-doc/scripts/generate_code_doc.py \
  --project /path/to/project \
  --files code_files_list.json \
  --output 源代码文档.docx \
  --software-name "软件名称" \
  --version "V1.0" \
  --lines-per-page 50 \
  --max-pages 65
```

### 使用说明书
```bash
# 1. 逐章生成JSON内容
# 2. 使用generate_manual.py生成各章Word
python3 ~/.hermes/skills/productivity/ruanzhu-doc/scripts/generate_manual.py \
  --content chapter1.json \
  --output 第1章.docx \
  --images-dir /path/to/screenshots

# 3. 使用merge_chapters.py合并
python3 ~/.hermes/skills/productivity/ruanzhu-doc/scripts/merge_chapters.py \
  --chapters 第1章.docx 第2章.docx ... \
  --output 说明书.docx \
  --software-name "软件名称" \
  --version "V1.0"
```

## 没有模板时的降级方案

如果没有Word模板，使用python-docx直接创建：
```python
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn

doc = Document()
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(16)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
# ... 添加内容 ...
doc.save("output.docx")
```

## 检查清单

- [ ] 所有输出文件扩展名是.docx
- [ ] 使用了skill中的Python脚本
- [ ] python-docx已安装
- [ ] 没有使用write_file输出.md格式的文档内容
