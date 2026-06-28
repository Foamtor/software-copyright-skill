# 软著说明书Word格式规范

参考文档：`/home/buqx/软著参考/说明书-农村宅基地管理信息系统V1.0 -（改）.docx`

## 封面格式

| 元素 | 字号 | 字体 | 加粗 | 对齐 |
|------|------|------|------|------|
| 软件名称 | 22pt (279400 EMU) | 黑体 | 是 | 居中 |
| 用户手册 | 22pt (279400 EMU) | 黑体 | 是 | 居中 |
| 著作权人 | 16pt (203200 EMU) | 宋体 | 否 | 居中 |
| 日期 | 16pt (203200 EMU) | 宋体 | 否 | 居中 |

封面中间需要空行分隔（约6行）。

## 标题格式

| 级别 | 样式名 | 字号 | 字体 | 加粗 | 行距 |
|------|--------|------|------|------|------|
| 一级标题 | Heading 1 | 16pt | 黑体 | **否** | 单倍行距 |
| 二级标题 | Heading 2 | 16pt | 默认 | **是** | 默认 |
| 三级标题 | Heading 3 | 默认 | 默认 | 否 | 默认 |

**重要**：一级标题（Heading 1）在参考文档中是**不加粗**的！

## 正文格式

| 元素 | 样式名 | 字号 | 字体 | 首行缩进 | 行距 |
|------|--------|------|------|----------|------|
| 正文段落 | 正文内容 | 16pt | Times New Roman + 宋体(eastAsia) | 426720 EMU (约2字符) | 1.5倍 |

## 图片说明格式

| 元素 | 字号 | 字体 | 对齐 | 行距 |
|------|------|------|------|------|
| 图片说明 | 16pt | Times New Roman + 宋体(eastAsia) | 居中 | 1.5倍 |

格式：`图X xxx示意`（如"图1 登录界面"）

## 页眉格式

| 位置 | 内容 | 字号 | 字体 |
|------|------|------|------|
| 左上角 | 软件名称+版本号 | 9pt | 宋体 |
| 右上角 | 页码（PAGE域代码） | - | - |

## EMU换算参考

```
426720 EMU ≈ 2字符首行缩进
203200 EMU = 16pt
279400 EMU = 22pt
```

## Python代码示例

```python
from docx.shared import Pt, Emu
from docx.oxml.ns import qn

# 设置正文格式
para = doc.add_paragraph()
para.paragraph_format.first_line_indent = Emu(426720)  # 首行缩进2字符
para.paragraph_format.line_spacing = 1.5

run = para.add_run("正文内容")
run.font.name = 'Times New Roman'
run.font.size = Pt(16)
run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# 设置一级标题（不加粗）
h1 = doc.add_heading("一、系统登录", level=1)
h1.paragraph_format.line_spacing = 1.0
for run in h1.runs:
    run.font.name = '黑体'
    run.font.size = Pt(16)
    run.bold = False
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

# 设置二级标题（加粗）
h2 = doc.add_heading("（一）新建项目", level=2)
for run in h2.runs:
    run.font.size = Pt(16)
    run.bold = True
```
