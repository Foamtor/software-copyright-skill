# python-docx Word 文档操作要点

## 核心原则：run级别替换

```python
# ❌ 错误：整体替换会丢失格式
para.text = para.text.replace('{{占位符}}', '新内容')

# ✅ 正确：遍历run替换，保持字体/字号/颜色
for run in para.runs:
    if '{{占位符}}' in run.text:
        run.text = run.text.replace('{{占位符}}', '新内容')
```

## 页眉页脚设置

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_page_field(paragraph):
    """插入PAGE域代码显示页码"""
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run1 = paragraph.add_run()
    run1._element.append(fldChar1)
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = ' PAGE '
    run2 = paragraph.add_run()
    run2._element.append(instrText)
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run3 = paragraph.add_run()
    run3._element.append(fldChar2)
```

## 中文字体设置

```python
# 必须设置eastAsia属性，否则中文显示为默认字体
run.font.name = 'Times New Roman'
run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
```

## 图片插入

```python
from docx.shared import Inches

# 清空占位符文本后插入图片
para.text = ''
run = para.add_run()
run.add_picture('image.png', width=Inches(5))
```

## 代码每页行数控制

```python
for i, line in enumerate(lines):
    para = doc.add_paragraph(line)
    # 每N行插入分页符
    if (i + 1) % lines_per_page == 0 and i < len(lines) - 1:
        doc.add_page_break()
```

## 注意事项

1. `.doc` 格式不兼容 python-docx，需先转为 `.docx`
2. 表格合并单元格处理较复杂，需检查cell是否被合并
3. 页眉页脚需要遍历 `doc.sections` 设置
4. 样式继承：模板定义样式，脚本只做内容注入
