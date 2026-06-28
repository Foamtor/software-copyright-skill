# Brand Profile 设计模式

## 概念来源

借鉴 [brand-docs](https://github.com/brand-docs) (195⭐) 的核心概念：
- **IntermediateDocument**: 纯语义JSON，不含格式信息
- **Brand Profile**: JSON格式的样式定义，可复用、可版本控制
- **确定性引擎**: 相同输入 → 相同输出

## 与 docxtpl 的对比

| 维度 | docxtpl (当前) | Brand Profile (借鉴) |
|------|----------------|---------------------|
| 格式定义 | Word模板 (.docx) | JSON配置文件 |
| 渲染引擎 | Jinja2模板引擎 | 确定性引擎 |
| 格式一致性 | 依赖模板质量 | 100%确定性 |
| 可版本控制 | 二进制文件diff困难 | JSON文本diff容易 |

## 实现方式

我们**部分借鉴**了Brand Profile概念：
- ✅ 将格式定义从Word模板迁移到JSON (`config/brand_profile.json`)
- ✅ 支持Brand Profile和旧格式两种配置
- ❌ 没有实现确定性引擎（继续使用docxtpl）

## Brand Profile 结构

```json
{
  "brand_info": { "name": "...", "version": "..." },
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
# 使用Brand Profile
python3 scripts/generate_manual.py \
  --config config/brand_profile.json ...

# 使用旧格式（兼容）
python3 scripts/generate_manual.py \
  --config config/format_spec.json ...
```

## 兼容性

`brand_profile_to_format_spec()` 函数将Brand Profile转换为旧的format_spec格式，确保向后兼容。
