# docxtpl 渲染陷阱（实战经验）

## 背景

docxtpl 使用 Jinja2 模板引擎渲染 Word 文档，但渲染后的行为与预期有多个差异。这些是在手动验证中逐个发现的真实问题。

## 陷阱清单

### 1. Jinja2 标记变成空行

**现象**：`{% for section in sections %}` 等标记渲染后变成空段落，导致标题间有多余空行。

**根因**：docxtpl 删除 Jinja2 标记内容，但保留段落本身。

**修复**：`post_process.py` 的 `remove_consecutive_empty_lines()` 删除连续空行。

### 2. 长段落首行缩进丢失

**现象**：content 字段中有 `\n` 换行，docxtpl 把整个内容放在一个段落中，只有第一行有首行缩进。

**根因**：docxtpl 不会根据 `\n` 自动分割段落。

**修复**：`post_process.py` 的 `split_long_paragraphs()` 按 `\n` 分割成独立段落，每个段落复制原段落格式。

### 3. 图名混在正文中无法单独设置格式

**现象**：图名（如"图8 系统总体架构图"）和正文在同一个段落中，无法单独设置 14pt 居中。

**根因**：content 字段中的图名是正文的一部分。

**修复**：`post_process.py` 的 `split_paragraph_at_figure_captions()` 用正则 `r'(图\d+\s+[^\n]+)'` 提取图名，创建独立段落并设置 14pt 居中。

### 4. 图片必须用 addprevious() 插入到图名上方

**现象**：用 `add_paragraph_after()` 插入图片，图片出现在图名下方。

**根因**：需求是"图片在图名上方"。

**修复**：用 `paragraph._element.addprevious(new_p)` 在图名段落**前**插入图片段落。

### 5. apply_formatting() 覆盖封面格式

**现象**：封面标题的居中、黑体、22pt 被正文格式覆盖。

**根因**：apply_formatting 遍历所有段落，没有跳过封面。

**修复**：找到第一个 Heading 1 的位置，之前的段落全部跳过。

### 6. 两端对齐导致中文字间距拉大

**现象**：正文字间距不均匀，某些行字间距很大。

**根因**：`align: justify`（两端对齐）在中文排版中会拉大字间距。

**修复**：正文使用 `align: left`（左对齐），图名使用 `align: center`（居中）。

### 7. content 字段中的图名导致重复

**现象**：图名出现两行（content 中一行，images 生成一行）。

**根因**：content 字段写入了图名，images 字段也生成图名。

**修复**：content 字段中**不要**写图名，图名只由脚本从 images 字段生成。

### 8. 模板中的图片列表循环生成文字列表

**现象**：文档中出现"图1 xxx\n图2 xxx\n..."的文字列表。

**根因**：模板中有 `{% for img in section.images %}{{img.ref}} {{img.description}}{% endfor %}`。

**修复**：模板中**不要**有图片列表循环，图名由 `post_process.py` 自动生成。

## 关键教训

1. **docxtpl 渲染后必须后处理** — 不能假设渲染结果就是最终结果
2. **段落格式要在渲染后应用** — 渲染会破坏模板中的格式
3. **封面段落要特殊保护** — apply_formatting 必须跳过封面
4. **图名必须独立段落** — 否则无法单独设置格式
5. **图片插入位置要精确** — 用 addprevious() 不是 addnext()
