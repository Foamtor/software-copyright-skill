---
name: software-copyright-skill
description: 生成中国软件著作权（软著）登记申请文档。LLM驱动：分析项目代码、生成内容；Python脚本辅助：模板填充、格式保持。
version: 4.6.0
author: Foamtor
homepage: https://github.com/Foamtor/software-copyright-skill
license: MIT
tags: [软著, 软件著作权, 文档生成, python-docx, Word, 版权登记, 模板填充]
---

# 软著文档生成 Skill（模板驱动版）

**核心原则**：模型输出JSON内容，脚本根据模板生成Word。格式100%由模板控制。

**版本**：V4.6（2026-06-27更新）

## 触发条件

用户提到：软著、软件著作权、软著申请、软著文档、信息采集表、使用说明书、设计说明、源代码文档

## 前置依赖

```bash
pip install python-docx docxtpl lxml Pillow
```

## 架构设计

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│  LLM 生成   │ ──→ │   content.json  │ ──→ │ docxtpl 渲染│
│  JSON 内容   │     │  (结构化数据)    │     │  生成.docx  │
└─────────────┘     └─────────────────┘     └─────────────┘
                                                  ↑
                                          templates/*.docx
                                          (格式由模板控制)
```

**关键原则**：
- 模型只输出JSON（内容），不接触格式
- 格式由Word模板（.docx）控制
- 用户给参考文档 → 提取格式 → 生成模板
- 格式变化 = 换模板，不需要改代码

## 配置格式

**支持两种配置格式**（`generate_manual.py` 自动检测）：

1. **Brand Profile**（推荐）：`config/brand_profile.json`
   - 包含样式定义、内容规则、写作风格
   - 可复用于多文档，易于版本控制
   - 详见 `references/brand-profile-design.md`

2. **旧格式**（兼容）：`config/format_spec.json`
   - 扁平的样式定义
   - 仍然支持，但建议迁移

```bash
# 使用Brand Profile
python3 scripts/generate_manual.py --config config/brand_profile.json ...

# 使用旧格式
python3 scripts/generate_manual.py --config config/format_spec.json ...
```

## ⚠️ 职责分工：模型 vs 脚本

**核心设计：模型负责生成和审阅，脚本负责验证和控制。**

| 任务 | 执行者 | 说明 |
|------|--------|------|
| 扫描项目结构 | 🐍 脚本 | `scan_project.py` |
| 生成大纲 | 🤖 模型 | 使用 `prompts/大纲生成.md` |
| 生成章节内容 | 🤖 模型 | 使用 `prompts/章节生成.md` |
| 审阅章节质量 | 🤖 模型 | 使用 `prompts/章节审阅.md` |
| 检查基础质量 | 🐍 脚本 | `review_chapter.py`（字数、数量） |
| 合并章节 | 🐍 脚本 | `merge_chapters.py` |
| 验证内容质量 | 🐍 脚本 | `validate_content_quality.py` |
| 生成Word文档 | 🐍 脚本 | `generate_manual.py` |
| 验证格式 | 🐍 脚本 | `validate_output.py` |
| 生成架构图 | 🤖+🐍 | excalidraw skill 生成JSON → render为PNG |
| 插入图片 | 🐍 脚本 | `generate_manual.py --image-dir` |

## ⚠️ 内容质量规范

### 写作风格

**软著说明书是用户操作指南，不是技术文档！**

#### 正确写法
```
在系统首页，点击"新建项目"按钮，弹出新建项目对话框。如下图。
图3 新建项目按钮

在对话框中填写项目名称和项目描述，点击"确定"按钮，即可创建新项目。如下图。
图4 新建项目对话框
```

#### 错误写法
```
一、项目管理功能：支持创建和管理项目，提供项目状态监控和版本控制能力。
```

### 内容质量要求

| 要求 | 标准 | 检查方式 |
|------|------|----------|
| **总字数** | ≥15000字 | 🐍 `validate_content_quality.py` |
| **章节数** | 6-10章 | 🐍 `validate_content_quality.py` |
| **图片标记** | ≥13张（精简版） | 🐍 `validate_content_quality.py` |
| **每章字数** | ≥1500字 | 🐍 `review_chapter.py` |
| **每节字数** | ≥300字 | 🐍 `review_chapter.py` |
| **每节images** | ≥1张 | 🐍 `review_chapter.py` |
| **写作风格** | 用户操作指南 | 🤖 模型审阅（第一章跳过） |

### 写作要点

1. **面向用户操作**：描述用户点击什么按钮、填写什么内容、看到什么结果
2. **语言简洁**：面向普通用户，不使用技术术语
3. **必须有"平台总体介绍"章节**：第一章必须是平台总体介绍，包含：功能概述、总体架构、技术实现、数据流向
   - ⚠️ 第一章是介绍性内容，不适用"用户操作指南"风格检查
   - ⚠️ 第一章使用 `review_chapter.py --is-chapter1` 跳过写作风格检查

### 配图策略（精简版）

**核心原则**：只配必要的图，不配装饰性图

#### 配图数量标准
| 类型 | 数量 | 来源 |
|------|------|------|
| 系统总体架构图 | 1张 | 绘制（excalidraw） |
| 功能模块截图 | 12-15张 | 截图（实际系统） |
| **总计** | **13-16张** | - |

#### 配图规则
1. **每个功能模块配1-2张代表性截图**，不要为细节操作配图
2. **不要配图的情况**：重复界面、弹窗提示、辅助功能
3. **第一章使用excalidraw生成架构图**，不要用matplotlib
4. **图名格式**：14pt字体、居中对齐（由post_process.py自动处理）
5. **图片位置**：图片插入到图名**上方**（不是下方）

#### 各章配图建议
| 章节 | 必须配图 | 可选配图 |
|------|----------|----------|
| 第一章：总体介绍 | 架构图、首页截图 | 功能入口截图 |
| 第二章：登录与首页 | 登录页面、首页布局 | 搜索功能 |
| 第三章：展览展会 | 展会列表、展会详情 | 展品详情 |
| 第四章：帮扶服务 | 帮扶列表、帮扶申请 | 帮扶记录 |
| 第五章：AI顾问 | AI对话页面、聊天历史 | 推荐内容 |
| 第六章：地图查询 | 地图页面、位置搜索 | 导航功能 |
| 第七章：个人中心 | 个人中心、设置页面 | 收藏管理 |

#### 配图位置规则
```
✅ 正确：正文描述 → "如下图。" → 图片 → 图名
❌ 错误：图片列表、图片在图名下方、图片与正文分离
```

**详细说明**：见 `references/配图生成最佳实践.md`

### JSON输出格式

**content.json必须包含以下字段**：

```json
{
  "software_name": "国农臻汇APP",
  "version": "V1.0",
  "company": "农业农村部乡村振兴监测中心",
  "cover": {
    "title": "国农臻汇APPV1.0",
    "subtitle": "用户使用手册",
    "company": "农业农村部乡村振兴监测中心",
    "date": "2025年9月"
  },
  "sections": [
    {
      "heading": "一、平台总体介绍",
      "content": "",
      "images": [],
      "subsections": [
        {
          "heading": "（一）平台功能概述",
          "content": "正文内容（不要包含图名）...",
          "images": [
            {"ref": "图8", "description": "系统总体架构图", "path": "系统总体架构图.png"}
          ]
        }
      ]
    }
  ]
}
```

**⚠️ 关键规则**：

1. **sections必须是层级结构**：一级标题（一、二、三...）→ subsections（（一）（二）...）
2. **不要把图名写在content字段中** — 图名由脚本从images字段自动生成
3. **images字段只保留有实际图片的图号** — 没有图片的不要写进去
4. **不需要notes字段** — 注意事项已去掉
5. **images中的path字段** — 指向实际图片文件名（在image-dir目录中）

**⚠️ 模板结构**

模板只包含heading和content，**不要**包含图片列表和注意事项循环：

```
✅ 正确模板：
{% for section in sections %}
{{section.heading}}
{{section.content}}
{% for sub in section.subsections %}
{{sub.heading}}
{{sub.content}}
{% endfor %}
{% endfor %}

❌ 错误模板（不要用）：
{% for img in section.images %}
{{img.ref}} {{img.description}}   ← 这会生成图片列表
{% endfor %}
{% for note in section.notes %}
注意：{{note}}                    ← 这会生成注意事项列表
{% endfor %}
```
❌ 错误模板（不要用）：
{% for img in section.images %}
{{img.ref}} {{img.description}}   ← 这会生成图片列表
{% endfor %}
{% for note in section.notes %}
注意：{{note}}                    ← 这会生成注意事项列表
{% endfor %}
```

## 三份文档规格

### 1. 信息采集表
- 使用 `fill_template.py` 填充模板
- 模板：`templates/info_template.docx`

### 2. 使用说明书
- 使用 `generate_manual.py` 生成
- 模板：`templates/manual_template_standard.docx`
- 模型输出：`content.json`
- **⚠️ 内容字数要求：≥15000字**

### 3. 源代码文档
- 使用 `generate_code_doc.py` 生成
- 每页≥50行，前30页+后30页，共60页

## 工作流程

### 阶段0：模板准备
1. 检查是否有用户提供的参考文档
2. 如果有：运行 create_template.py 提取格式，生成模板
3. 如果没有：使用默认模板 `templates/manual_template_standard.docx`

### 阶段1：项目分析
1. 运行 scan_project.py 扫描项目结构
2. 阅读关键文件（README、路由、主入口）
3. 理解功能模块和业务逻辑

### 阶段2：信息采集
1. 从项目中提取软件名称、版本号、功能模块
2. 展示给用户确认
3. 生成 info.json

### 阶段3：大纲生成
1. 🤖 模型根据功能模块生成三级目录大纲
2. 用户审阅确认
3. 生成 outline.json

### 阶段4：内容生成（迭代循环）

**⚠️ 核心流程：生成 → 验证 → 修改 → 再验证（直到通过）**

```
┌─────────────────────────────────────────────────────────────┐
│ 第1轮：生成                                                  │
│  1. 🤖 模型按章节分步生成JSON内容（使用 prompts/章节生成.md） │
│  2. 🐍 脚本检查每章基础质量（review_chapter.py）              │
│  3. 🐍 脚本验证整体内容质量（validate_content_quality.py）    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 第2轮：修改（如果验证不通过）                                 │
│  4. 🤖 模型根据验证报告补充内容                               │
│     - 字数不足：补充详细描述                                  │
│     - 配图不足：补充图片标记                                  │
│  5. 🐍 脚本再次验证内容质量                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 第N轮：重复修改直到验证通过                                   │
│  6. 🐍 脚本合并所有章节（merge_chapters.py）                  │
│  7. 🐍 生成架构图（excalidraw skill → render_excalidraw.py）  │
└─────────────────────────────────────────────────────────────┘
```

**验证标准（精简版）：**
| 指标 | 要求 | 检查脚本 |
|------|------|----------|
| 总字数 | ≥15000字 | validate_content_quality.py |
| 章节数 | 6-10章 | validate_content_quality.py |
| 配图数量 | ≥13张 | validate_content_quality.py |
| 每章字数 | ≥1500字 | review_chapter.py |
| 每节字数 | ≥300字 | review_chapter.py |

**修改策略：**
1. **字数不足**：补充详细描述，增加操作步骤、注意事项
2. **配图不足**：在关键操作处添加"如下图"和图片标记
3. **章节不足**：拆分或合并章节，保持6-10章

### 阶段5：文档生成
```bash
# 一步完成：生成+后处理
python3 scripts/generate_manual.py \
  --content content.json \
  --template templates/manual_template_standard.docx \
  --output output/说明书.docx \
  --config config/brand_profile.json \
  --image-dir images/
```

**generate_manual.py 已集成后处理**，自动完成：
1. 分割长段落（确保首行缩进）
2. 分割图名成独立段落（14pt居中）
3. 在图名上方插入图片
4. 删除连续空行
5. 替换页眉页脚占位符，添加页码
6. 应用格式（跳过封面段落）

**⚠️ 独立后处理脚本**：`post_process.py` 仍然可用，用于对已有文档进行后处理。

### 阶段6：审阅提交
1. 检查三份文档完整性
2. 统计页数、字数
3. 🐍 检查内容质量指标
4. 生成提交清单

## 脚本清单

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `generate_manual.py` | 生成说明书（含后处理） | content.json + 模板 | 说明书.docx |
| `post_process.py` | 独立后处理脚本 | 说明书_raw.docx + content.json | 说明书.docx |
| `review_chapter.py` | 单章质量检查 | chapter.json | 检查结果（支持 `--is-chapter1`） |
| `validate_content_quality.py` | 内容质量验证 | content.json 或 chapters/ | 验证报告 |
| `validate_output.py` | 格式验证 | 说明书.docx | 验证报告 |
| `merge_chapters.py` | 合并章节 | chapters/ | content.json |
| `scan_project.py` | 扫描项目结构 | 项目路径 | project_info.json |
| `create_template.py` | 从参考文档创建模板 | 参考.docx | 模板.docx |
| `create_standard_template.py` | 创建标准模板 | format_spec.json | 模板.docx |
| `fill_template.py` | 填充信息采集表 | info.json + 模板.docx | 采集表.docx |
| `generate_code_doc.py` | 生成代码文档 | 项目路径 | 代码文档.docx |
| `utils.py` | 公共工具函数库 | - | 被其他脚本导入 |
| `test_generate.py` | TDD测试套件 | - | 测试结果 |

### 测试脚本

| 脚本 | 功能 | 运行方式 |
|------|------|----------|
| `scripts/test_generate.py` | TDD测试套件 | `python3 scripts/test_generate.py` |

**测试覆盖**：
- 单元测试：count_chars, extract_figure_refs, has_figure_caption, validate_content, brand_profile_loading, brand_profile_to_format_spec
- 集成测试：generate_manual.py完整流程
- 验收测试：文档符合Brand Profile规范

## 使用示例

```bash
# 1. 扫描项目
python3 scripts/scan_project.py --path /path/to/project --output project_info.json

# 2. 生成文档（一步完成：生成+后处理）
python3 scripts/generate_manual.py \
  --content content.json \
  --template templates/manual_template_standard.docx \
  --output output/说明书.docx \
  --config config/brand_profile.json \
  --image-dir images/

# 3. 验证格式
python3 scripts/validate_output.py --docx output/说明书.docx

# 4. 验证内容质量
python3 scripts/validate_content_quality.py --content content.json

# 5. 检查单章质量（第一章使用 --is-chapter1 标志）
python3 scripts/review_chapter.py --chapter chapters/chapter1.json --is-chapter1
python3 scripts/review_chapter.py --chapter chapters/chapter2.json

# 6. 运行TDD测试
python3 tests/test_generate.py
```

## ⚠️ 关键规则（按优先级排序）

### P0：绝对规则
1. **必须输出.docx** — 绝对不要输出.md文件
2. **模型只输出JSON** — 不要让模型直接生成Word内容
3. **格式由模板控制** — 不要在JSON中包含格式信息
4. **content.json必须包含cover字段** — 否则封面标题为空
5. **模板不要有图片列表和注意事项循环** — 使用 `manual_template_standard.docx`

### P1：内容质量规则
6. **写作风格** — 必须是用户操作指南风格，不是技术文档
7. **分步生成** — 说明书必须按章节分步生成，每章自动审阅后再继续

### P2：流程规则
8. **上下文传递** — 每章生成时传入前几章摘要，保持内容一致性
9. **断点续传** — 每章保存到独立JSON文件，中断后可从上次位置继续
10. **验证输出** — 生成后必须用validate_output.py验证格式

## ⚠️ 致命陷阱（必须避免）

这些是手动验证中发现的真实bug，每个都会导致文档格式崩溃：

### P0：绝对致命

| # | 陷阱 | 后果 | 正确做法 |
|---|------|------|----------|
| 1 | **模板有图片列表循环** `{% for img %}` | 文档出现"图1 xxx"文字列表 | 模板不要有图片循环，图名由脚本生成 |
| 2 | **模板有注意事项循环** `{% for note %}` | 文档出现"注意事项：xxx" | 模板不要有注意事项循环 |
| 3 | **content字段中写图名** | 图名重复两行 | 图名只在images字段，不在content中 |
| 4 | **content字段中写注意事项** | 注意事项无法删除 | content中不要写"注意事项：" |
| 5 | **sections没有层级** | 缺少"一、平台总体介绍"标题 | sections必须是一、→（一）→（二）层级 |
| 6 | **图片插入到图名下方** | 图片位置错误 | 用 `addprevious()` 在图名**上方**插入 |
| 7 | **apply_formatting覆盖封面** | 封面格式被破坏 | 跳过第一个Heading 1之前的段落 |

### P1：格式问题

| # | 陷阱 | 后果 | 正确做法 |
|---|------|------|----------|
| 8 | **Jinja2标记变空行** | 标题间有多余空行 | `post_process.py` 删除连续空行 |
| 9 | **长段落不分割** | 首行缩进丢失 | `post_process.py` 分割长段落 |
| 10 | **图名混在正文中** | 无法单独设置格式 | `post_process.py` 分割图名成独立段落 |
| 11 | **两端对齐** | 中文字间距被拉大 | 正文用左对齐(left)，不用justify |
| 12 | **页眉页脚占位符未替换** | 显示"{software_name}" | `replace_header_footer()` 替换 |

### P2：内容问题

| # | 陷阱 | 后果 | 正确做法 |
|---|------|------|----------|
| 13 | **图片只保留有实际文件的** | 空图片标记 | images字段只放有path的图号 |
| 14 | **用matplotlib生成架构图** | 样式不专业 | 用excalidraw skill生成 |
| 15 | **为小板块单独配图** | 图片过多 | 按功能模块整体配图，精简到13-16张 |
| 16 | **content.json缺少software_name** | 封面标题为空 | 必须有cover.title或software_name |

**详见**：`references/V4.3验证问题清单.md` — 16个问题的完整修复方案

## 常见问题与解决方案

详见 `references/常见问题与解决方案.md`

## 参考文档

- `references/brand-profile-design.md` — **新增**：Brand Profile设计（借鉴brand-docs）
- `references/专业审阅报告-V4.4.md` — **必读**：专业审阅报告，设计评分、优化路线图
- `references/短期优化结果.md` — 短期优化完成情况，utils.py函数清单
- `references/docxtpl后处理必知必会.md` — **必读**：后处理逻辑、content.json规则、模板设计原则
- `references/V4.3验证问题清单.md` — 手动验证发现的16个问题及修复方案
- `references/常见问题与解决方案.md` — 所有已知问题和修复方案
- `references/配图生成最佳实践.md` — 配图方案（excalidraw > matplotlib）
- `references/模板驱动架构设计.md` — docxtpl方案详解
- `references/内容质量保障规范.md` — 内容质量指标、写作风格
