# Brand Profile 设计文档

## 概念来源

借鉴 [brand-docs](https://github.com/brand-docs)（195⭐）的核心概念：
- **IntermediateDocument**：纯语义JSON，不含格式信息
- **Brand Profile**：JSON格式的样式定义，可复用、可版本控制
- **确定性引擎**：相同输入 → 相同输出

## 与旧格式对比

| 维度 | 旧格式 (format_spec.json) | Brand Profile |
|------|---------------------------|---------------|
| 结构 | 扁平的样式定义 | 分层的样式+规则+风格 |
| 复用性 | 低（每个项目独立） | 高（可跨项目复用） |
| 可读性 | 中 | 高 |
| 扩展性 | 低 | 高（可添加新字段） |

## Brand Profile 结构

```json
{
  "brand_info": {
    "name": "农业农村部乡村振兴监测中心",
    "description": "软著说明书标准格式"
  },
  "styles": {
    "cover_title": { "font": {...}, "paragraph": {...} },
    "heading1": { "font": {...}, "paragraph": {...} },
    "body": { "font": {...}, "paragraph": {...} },
    "figure_caption": { "font": {...}, "paragraph": {...} }
  },
  "content_rules": {
    "min_total_chars": 15000,
    "min_chapter_chars": 1500,
    "min_images": 13
  },
  "writing_style": {
    "type": "user_guide",
    "rules": [...]
  }
}
```

## 使用方式

```bash
# generate_manual.py 自动检测配置格式
python3 scripts/generate_manual.py \
  --config config/brand_profile.json \
  --content content.json \
  --output output.docx
```

## 转换函数

`utils.py` 提供 `brand_profile_to_format_spec()` 函数，将Brand Profile转换为旧格式以保持兼容。

## 设计原则

1. **样式与内容分离** — Brand Profile只定义样式，不包含内容
2. **可复用** — 同一品牌的多文档可以共享Brand Profile
3. **可版本控制** — JSON格式易于diff和merge
4. **向后兼容** — 自动检测格式，支持旧格式
