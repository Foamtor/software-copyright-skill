# 阶段0：模板准备

## 目标

准备Word模板，作为后续生成文档的基础。

## 流程

### 1. 检查用户参考文档

```
用户：这是参考格式，请按照这个生成
Agent：收到，我来分析参考文档的格式
```

### 2. 提取格式配置

```bash
python3 scripts/create_template.py \
  --ref /path/to/参考文档.docx \
  --output templates/user_template.docx \
  --auto
```

脚本会分析：
- 页面设置（纸张大小、页边距）
- 样式定义（Heading 1/2/3、正文、图名）
- 字体字号（黑体16pt、宋体16pt等）
- 段落格式（缩进、行距、段前段后）
- 页眉页脚

### 3. 创建模板

提取格式后，需要在Word中手动添加Jinja2占位符：

```
封面页：
  {{cover_title}}        ← 软件名称
  {{cover_company}}      ← 公司名称
  {{cover_date}}         ← 日期

正文页：
  {% for section in sections %}
  {{section.heading}}    ← 章节标题
  {{section.content}}    ← 正文内容
  
  {% for img in section.images %}
  {{img.ref}} {{img.description}}  ← 图片说明
  {% endfor %}
  
  {% for note in section.notes %}
  注意：{{note}}         ← 注意事项
  {% endfor %}
  
  {% for sub in section.subsections %}
  {{sub.heading}}        ← 子章节标题
  {{sub.content}}        ← 子章节内容
  {% endfor %}
  {% endfor %}
```

### 4. 用户确认

展示模板配置：
```
已从参考文档提取格式：
- 页面：A4，上下2.54cm，左右3.17cm
- 标题：黑体，16pt，不加粗
- 正文：Times New Roman，16pt，首行缩进1.18cm
- 行距：1.5倍
- 页眉：宋体9pt

请确认是否正确。
```

### 5. 使用默认模板

如果用户没有参考文档，使用默认模板：
```bash
# 默认模板已预置在 templates/manual_template.docx
# 格式符合软著申请标准
```

## 输出

- `templates/manual_template.docx` — 说明书模板
- `templates/code_template.docx` — 代码文档模板
- `templates/info_template.docx` — 信息采集表模板

## 注意事项

1. **模板是格式的唯一来源** — 所有格式信息都在模板中，JSON只包含内容
2. **Jinja2标签要正确** — 标签错误会导致渲染失败
3. **保留原始样式** — 从参考文档创建模板时，保留原有样式定义
4. **测试模板** — 创建模板后，用测试数据验证渲染效果
