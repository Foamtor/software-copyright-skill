---
name: software-copyright-skill
description: 生成中国软件著作权（软著）登记申请文档。LLM驱动：分析项目代码、生成内容、交互式填写；Python脚本辅助：模板填充、格式保持、代码提取。适用于各类AI Agent（Hermes、Claude Code、Cursor、Codex、OpenClaw等）。
metadata:
  author: Foamtor
  version: 1.0.0
  homepage: https://github.com/Foamtor/software-copyright-skill
license: MIT
---

# 软著文档生成 Skill（LLM驱动版）

核心原则：**大模型负责理解和生成内容，Python脚本负责文件IO和格式操作。**

## 触发条件

用户提到：软著、软件著作权、软著申请、软著文档、信息采集表、使用说明书、设计说明、源代码文档

## 前置依赖

### Python包

```bash
pip install python-docx lxml Pillow olefile -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> **注意**：`olefile` 用于读取旧版 `.doc` 格式文件（python-docx 只支持 `.docx`）。

### 配图生成（推荐使用Excalidraw）

```bash
# 安装 Excalidraw Diagram Skill（如果未安装）
# 方式1：通过 skills CLI
npx skills add coleam00/excalidraw-diagram-skill

# 方式2：手动安装
git clone https://github.com/coleam00/excalidraw-diagram-skill.git
cp -r excalidraw-diagram-skill ~/.agents/skills/excalidraw-diagram

# 配置渲染环境（需要 uv）
cd ~/.agents/skills/excalidraw-diagram/references
uv sync -i https://pypi.tuna.tsinghua.edu.cn/simple
uv run playwright install chromium
```

> **国内镜像**：如果 `uv sync` 下载慢，可设置环境变量：
> ```bash
> export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
> ```

## 设计原则

**LLM是大脑，Python是手脚**：
- LLM负责：理解代码、生成内容、决定策略、响应用户反馈
- Python负责：文件IO、格式操作、代码扫描、模板填充
- 不要让Python硬编码生成内容，也不要让LLM直接操作Word格式

**分步生成，自动审阅**：
- 长文档必须分步生成，防止中断
- **用户只审阅大纲**，章节内容由agent自动审阅
- 大纲先行（三级目录），用户确认后再填充内容
- 每章生成时传入前几章摘要，保持前后一致
- 最终完成后用户审阅整个文档

## 架构设计

```
大模型（大脑）                    Python脚本（手脚）
├── 分析项目代码结构               ├── 扫描目录、统计代码行数
├── 理解功能模块和技术栈           ├── 读取Word模板、识别占位符
├── 生成采集表各字段内容           ├── 替换占位符（run级别，保持格式）
├── 撰写说明书文字描述             ├── 插入图片到指定位置
├── 决定代码提取策略               ├── 设置页眉页脚
└── 根据用户反馈修订内容           └── 控制分页和每页行数
```

**关键原则**：样式与内容分离。Word模板定义所有样式，大模型只生成纯文本/JSON，Python脚本做占位符替换。`run.text` 级别替换，不改变 `run.font` 等样式属性。

## ⚠️ 关键格式规范（必须严格遵守）

### Word格式规范

| 元素 | 格式要求 |
|------|----------|
| **封面标题** | 22pt，黑体，加粗，居中 |
| **封面公司/日期** | 16pt，宋体，**加粗**，居中，在页面底部（封面最后两行） |
| **一级标题（Heading 1）** | 黑体，16pt，**不加粗**，首行缩进1.18cm，两端对齐，1.5倍行距，段前段后0 |
| **二级标题（Heading 2）** | 黑体，16pt，**不加粗**，首行缩进1.18cm，两端对齐，1.5倍行距，段前段后0 |
| **三级标题（Heading 3）** | 默认字体，默认字号 |
| **正文** | 样式名：正文内容，Times New Roman，16pt，首行缩进1.18cm，两端对齐，1.5倍行距，段前段后0 |
| **图片说明** | Times New Roman，14pt（4号字），居中，段前段后0，格式：图X xxx示意 |
| **页眉** | 左：软件名称+版本号，右：页码（9pt，宋体，使用多个空格推到右侧） |
| **文字颜色** | 所有文字均为黑色（RGB: 0,0,0） |

### EMU换算

- 426720 EMU ≈ 2字符首行缩进
- 203200 EMU = 16pt
- 279400 EMU = 22pt

## ⚠️ 写作风格规范（必须严格遵守）

**软著说明书是用户操作指南，不是技术文档！**

### 正确写法（参考文档风格）
```
在系统首页，点击"新建项目"按钮，弹出新建项目对话框。如下图。
图3 新建项目按钮

在对话框中填写项目名称和项目描述，点击"确定"按钮，即可创建新项目。如下图。
图4 新建项目对话框
```

### 错误写法（技术架构风格）
```
一、项目管理功能：支持创建和管理农业调查数据治理项目，实现数据治理工作的规范化管理，
提供项目状态监控和版本控制能力。
```

### 写作要点

1. **面向用户操作**：描述用户点击什么按钮、填写什么内容、看到什么结果
2. **按功能模块组织**：一、二、三大章，（一）（二）小章，1. 2. 3. 三级
3. **截图配文字**：每段操作描述后跟"如下图。"，然后是"图X xxx示意"
4. **语言简洁**：面向普通用户，不使用技术术语
5. **图文结合**：截图位置用"图X xxx"标记，居中显示
6. **操作步骤**：按用户操作顺序组织，不是按系统功能模块
7. **⚠️ 每个功能必须有"注意事项"**：每个二级标题下的功能模块，操作描述后必须列出注意事项，提醒用户常见问题和操作要点
8. **⚠️ 必须有"平台总体介绍"章节**：第一章必须是平台总体介绍，包含：功能概述、总体架构、技术实现、数据流向，每个部分都需要配图

### 章节结构示例

```
一、平台总体介绍（必须有，第一章）
  （一）平台功能概述
  （二）总体架构
  （三）技术实现
  （四）数据流向
二、系统登录
  （操作描述 + 截图 + 注意事项）
三、项目管理
  （一）新建项目
    （操作描述 + 截图 + 注意事项）
  （二）项目列表
    （操作描述 + 截图 + 注意事项）
四、数据导入
  （一）文件上传
  （二）数据预览
  ...
```

## 三份文档规格

### 1. 信息采集表

参考模板结构（2个表格）：

**表1：软件基本信息**（19行8列）
- 序号1-9：软件全称、简称、版本号、软件分类、作品说明、开发方式、著作权人、完成日期、发表状态
- 占位符格式：`{{软件全称}}`、`{{版本号}}` 等

**表2：开发与运行环境**（15行4列）
- 硬件环境、操作系统、开发工具、编程语言、源程序量
- 功能特点：开发目的、核心功能（每项有字数限制，50字以内）

### 2. 使用说明书 或 设计说明（二选一）

| 使用说明书 | 设计说明 |
|------------|----------|
| 登录页面截图+描述 | 软件结构图 |
| 操作步骤+截图 | 功能流程图、逻辑框图 |
| 截图连贯，体现页面跳转 | 总体设计、接口设计 |
| 体现数据变化 | 模块/函数功能、算法、运行设计 |

**页数要求**：前30页+后30页，每页≥30行（图片除外），不足60页全部提交

### 3. 源代码文档

- 每页≥50行，前30页+后30页，共60页
- **实际提取按65页计算**（需考虑封面页等额外页数），生成后用脚本检查总行数是否足够
- 不足60页全部提交
- 提取顺序：主入口 → 路由 → 核心页面 → 公共组件 → API → 工具函数
- **排除第三方库**：扫描时排除 `node_modules/`、`.venv/`、`__pycache__/`、`dist/` 等目录

## 工作流程

### 阶段0：首次使用确认

```
1. 展示默认要求和模板结构
2. 询问用户：
   - 是否按默认要求执行？
   - 是否需要修改模板或要求？
3. 如果用户有自定义模板：
   - 读取模板，分析结构
   - 提取占位符列表
   - 确认填充方案
```

**如果用户提供自定义要求和参考文档**：
```
1. 读取用户提供的要求文档（markdown/text）
2. 分析参考Word文档结构（标题、样式、占位符）
3. 生成新的模板文件
4. 展示给用户确认
5. 保存到 {baseDir}/templates/ 目录
```

### 阶段1：项目分析

```bash
python3 {baseDir}/scripts/scan_project.py --path /项目路径 --output /tmp/project_info.json
```

**⚠️ 第一步：识别前端项目**
- 扫描项目根目录，列出所有前端相关目录
- 如果存在多个前端目录（如 `ui_desgin/`、`agent_app/`、`agent_ui/`），**必须先向用户确认**功能模块以哪个为准
- 典型分工：功能设计（ui_desgin）→ 功能模块定义；APP代码（agent_app）→ 技术架构

大模型阅读关键文件（README、package.json、路由、主入口），理解：
- 软件名称、版本号
- 功能模块列表
- 技术栈
- 业务逻辑

**Vue.js项目重点看**：`router/index.ts`（路由→功能模块）、`views/*.vue`（页面→具体功能）、`backend/src/services/`（后端→业务逻辑）、`README.md`。

### 阶段2：交互式信息采集

```
大模型：我从项目中检测到以下信息，请确认/修改：

| 字段 | 检测值 |
|------|--------|
| 软件全称 | xxx管理系统V1.0 |
| 编程语言 | Java、JavaScript |
| 主要功能 | 1.用户管理 2.数据查询 ... |
| 开发工具 | IDEA、VSCode |
| 运行环境 | CentOS 7、Java8、Docker |

请确认或指出需要修改的地方。

用户：xxx改成yyy，功能3改为...

大模型：已更新，再次确认...
（循环直到用户说"确认"）
```

用户确认后，准备信息采集表数据（JSON格式），调用模板填充：

```bash
python3 {baseDir}/scripts/fill_template.py \
  --template {baseDir}/templates/信息采集表模板.docx \
  --content /tmp/采集表内容.json \
  --output /output/信息采集表.docx
```

**采集表字段字数限制**：功能特点每项50字以内。详见 `{baseDir}/references/信息采集表填写要求.md`。

### 阶段3：使用说明书大纲生成（三级目录）

```
大模型：
"根据项目分析，我生成了使用说明书大纲（三级目录），请审阅：

一、平台总体介绍
  （一）平台功能概述
    1. 功能列表
    2. 用户端/管理端划分
  （二）总体架构
    1. 技术架构
    2. 部署架构
  （三）技术实现
  （四）数据流向

二、系统登录
  （一）登录入口
    1. 登录页面
    2. 登录流程
  （二）登录成功/失败处理

三、xxx功能
  （一）xxx
    1. xxx
    2. xxx
  ...

请确认大纲，或提出修改意见（如增删章节、调整顺序）。"

用户：第三章xxx功能需要拆分成两个子章节
大模型：已调整，更新后的大纲...
（循环直到用户确认）
```

### 阶段4：分章节生成说明书（自动审阅）

```
大模型：
"开始生成第一章内容。请提供第一章相关的截图：
- 登录页面截图
- 系统首页截图
..."

用户提供截图路径（或跳过，后续补充）

大模型生成第一章内容（JSON格式）

【自动审阅】大模型启动审阅角色，检查：
- 内容与大纲是否一致
- 描述是否准确、详细
- 术语与前几章是否一致
- 截图位置是否合理
- 是否有遗漏或错误

如果发现问题，自动修正后继续

调用脚本生成Word：
python3 {baseDir}/scripts/generate_manual.py \
  --content /tmp/第1章内容.json \
  --output /output/说明书_第1章.docx \
  --images-dir /output/images

记录本章摘要，传入下一章

继续生成下一章...（循环直到所有章节完成）
```

**上下文传递**：每章生成时，传入前几章的摘要，保持内容一致性。

**自动审阅机制**：
- 每章生成后，由agent自动审阅
- 检查内容一致性、准确性、完整性
- 发现问题自动修正
- 用户只在最终完成后审阅整个文档

**截图处理**：
- 在生成说明书内容时，使用 `[截图: xxx]` 标记截图位置
- 截图可以后续通过两种方式补充：
  - **模式B（推荐）**：用户预先截图放到文件夹，运行 `match_screenshots.py` 自动匹配
  - **模式A**：提供系统URL，运行 `auto_screenshot.py` 自动截图
- 匹配/截图完成后，使用 `generate_manual.py` 的 `--images-dir` 参数插入图片
- 详见 `{baseDir}/references/截图功能规范.md`

**JSON格式示例**：
```json
{
  "title": "二、系统登录",
  "sections": [
    {
      "heading": "（一）登录入口",
      "content": "在浏览器地址栏输入系统地址，进入登录页面。如下图。",
      "images": [{"filename": "login.png", "caption": "图3 系统登录页面"}],
      "notes": ["首次登录需使用管理员分配的账号密码"]
    }
  ]
}
```

### 阶段5：代码文档生成

```
大模型：
"根据项目分析，建议提取以下代码文件：

| 顺序 | 文件 | 原因 |
|------|------|------|
| 1 | Main.java | 主入口 |
| 2 | application.yml | 配置文件 |
| 3 | UserController.java | 核心业务 |
| ... | ... | ... |

请确认提取列表，或补充/删除文件。"

用户确认

python3 {baseDir}/scripts/generate_code_doc.py \
  --project /项目路径 \
  --files /tmp/文件列表.json \
  --output /output/代码文档.docx \
  --software-name "XXX系统V1.0" \
  --version "V1.0"
```

### 阶段6：最终审阅与合并

```
大模型：
"所有文档已生成，请最终审阅：
1. 信息采集表：xxx.docx
2. 使用说明书：xxx.docx（共X章）
3. 代码文档：xxx.docx

请确认是否有需要修改的地方。"

用户确认后，合并分章文档为完整说明书：

python3 {baseDir}/scripts/merge_chapters.py \
  --chapters /output/说明书_第1章.docx /output/说明书_第2章.docx ... \
  --output /output/使用说明书.docx \
  --software-name "XXX系统V1.0" \
  --version "V1.0"
```

### 阶段7：提交准备

```
大模型：
"文档已生成完成，现在创建提交清单：

1. 检查文档格式（字号、字体、缩进）
2. 验证信息采集表必填字段
3. 统计文档字数和页数
4. 生成提交清单（参考 {baseDir}/references/提交清单模板.md）

提交清单包含：
- 申请信息（软件名称、版本号、著作权人等）
- 提交材料清单（信息采集表、说明书、源代码文档）
- 提交步骤（在线填报、材料准备、提交申请）
- 注意事项（格式要求、常见问题）
- 联系方式和时间安排

用户确认后，保存提交清单到输出目录。"
```

**提交清单生成要点**：
1. 使用 `{baseDir}/references/提交清单模板.md` 作为模板
2. 根据实际生成的文档填充信息
3. 标注需要用户补充的内容（如系统截图）
4. 提供详细的提交步骤和注意事项

## 配图生成流程

### ⚠️ 配图方案选择（重要）

**不要使用Mermaid生成配图！** Mermaid生成的PNG存在以下问题：
- 图片尺寸不适合Word文档插入
- 字体太小，打印后可读性差
- 自动布局不适合A4纸排版
- 需要额外安装mermaid-cli

**matplotlib可以生成基础配图，但样式不够专业**：matplotlib生成的图存在以下问题：
- 样式不符合传统软件图风格（默认是数据可视化风格）
- 文字在打印时仍然偏小
- 插入Word时图片尺寸控制不够精确
- 缺少专业的软件架构图元素（如标准图标、连接线样式）

### ✅ 推荐方案：Excalidraw Diagram Skill（首选）

**必须使用 Excalidraw Diagram Skill 生成配图。** 该skill兼容AgentSkills标准，可通过以下方式安装：

```bash
# 方式1：通过 skills CLI（推荐）
npx skills add coleam00/excalidraw-diagram-skill

# 方式2：手动安装
git clone https://github.com/coleam00/excalidraw-diagram-skill.git
cp -r excalidraw-diagram-skill ~/.agents/skills/excalidraw-diagram
```

**渲染环境配置**：
```bash
cd ~/.agents/skills/excalidraw-diagram/references
uv sync -i https://pypi.tuna.tsinghua.edu.cn/simple
uv run playwright install chromium
```

**工作流程**：

```
1. 加载 excalidraw-diagram skill（阅读其SKILL.md了解设计方法论）
2. 根据项目信息，为每张配图设计Excalidraw JSON
3. 使用 render_excalidraw.py 渲染为PNG
4. 视觉验证循环：渲染→查看→修复→重新渲染（2-4次）
5. 使用 replace_docx_images.py 将PNG插入Word文档
```

**每张配图的生成流程**：
1. **设计**：根据excalidraw-diagram skill的设计方法论，将概念映射为视觉模式
2. **JSON**：手写Excalidraw JSON（不要用Python脚本生成）
3. **渲染**：调用 `render_excalidraw.py` 生成PNG
4. **验证**：查看PNG，检查文字溢出、重叠、对齐等问题
5. **修复**：修改JSON后重新渲染，重复2-4次直到满意
6. **插入**：使用 `replace_docx_images.py` 将PNG插入Word文档

### 配图类型与视觉模式

| 配图类型 | 说明 | Excalidraw视觉模式 |
|----------|------|-------------------|
| 架构图 | 系统总体架构，展示各层关系 | Assembly Line（分层结构）|
| 数据流向图 | 数据从输入到输出的完整流程 | Fan-Out / Convergence |
| 技术栈图 | 前后端技术栈展示 | Tree（树形结构）|
| 功能模块图 | 各功能模块及其子功能 | Side-by-Side + 层级连接 |

### 配图插入Word

配图生成后，使用 `replace_docx_images.py` 插入Word文档：

```bash
python3 {baseDir}/scripts/replace_docx_images.py \
  --docx /output/说明书.docx \
  --images-map /tmp/images_map.json \
  --output /output/说明书_含配图.docx
```

images_map.json 格式：
```json
{
  "image1.png": "/output/images/architecture.png",
  "image2.png": "/output/images/data_flow.png"
}
```

⚠️ **重要**：替换时不要创建 `.backup` 文件，否则会被打包进docx导致文件大小翻倍。

### 配图命名规范

| 配图 | 文件名 | 说明书中引用 |
|------|--------|-------------|
| 架构图 | architecture.excalidraw → .png | 图2 系统总体架构图 |
| 数据流向图 | data_flow.excalidraw → .png | 图4 数据流向图 |
| 技术栈图 | tech_stack.excalidraw → .png | 图3 技术栈示意图 |
| 功能模块图 | module.excalidraw → .png | 图1 平台功能架构图 |

### 配图样式规范

**尺寸要求**：
- 宽度：10英寸（适合A4纸打印）
- 高度：7.5英寸（架构图/模块图）或5英寸（流程图）
- 分辨率：300dpi

**Excalidraw设置**：
- `roughness: 0` — 清晰边缘，适合技术文档
- `strokeWidth: 2` — 标准线宽
- `opacity: 100` — 不使用透明度
- `fontFamily: 3` — Excalidraw默认字体

**中文字体**：WSL环境下优先使用 `WenQuanYi Zen Hei`（系统自带），其次 `SimHei`（可能未安装）。

### 备选方案（仅在Excalidraw不可用时使用）

如果Excalidraw Skill未安装或渲染环境不可用，可降级使用：

1. **D2 Language** ⭐⭐⭐⭐
   - 安装：`curl -fsSL https://d2lang.com/install.sh | sh -s --`
   - 语法简洁，输出精美

2. **matplotlib** ⭐⭐⭐（基础方案）
   - 安装：`pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple`
   - 使用 `{baseDir}/scripts/generate_diagrams.py` 生成
   - 样式不够专业，仅作为降级方案

> **详细调研报告**：见 `{baseDir}/references/图表工具调研报告.md`

## 脚本清单

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `scan_project.py` | 扫描项目结构 | 项目路径 | JSON（目录树、技术栈、文件列表） |
| `fill_template.py` | 模板占位符替换 | 模板docx + 内容JSON | 填充后的docx |
| `generate_manual.py` | 生成说明书章节 | 模板 + 内容JSON + 图片目录 | docx |
| `merge_chapters.py` | 合并章节文档 | 多个章节docx | 完整docx |
| `generate_code_doc.py` | 生成代码文档 | 项目路径 + 文件列表JSON | docx |
| `generate_template.py` | 生成自定义模板 | 用户要求 + 参考文档 | 新模板docx |
| `generate_diagrams.py` | 生成配图（matplotlib，降级方案） | 项目信息JSON + 输出目录 | PNG图片 |
| `replace_docx_images.py` | 替换docx中的图片 | 原docx + 图片映射 | 新docx |
| `match_screenshots.py` | 智能匹配截图到说明书章节 | 截图文件夹 + 说明书JSON | 匹配报告JSON |
| `auto_screenshot.py` | 自动截图（Playwright） | 系统URL + 登录信息 | 截图文件夹 + 结果JSON |

## ⚠️ 关键注意事项

1. **run级别替换** — 必须遍历 `para.runs` 替换，不能用 `para.text =` 整体替换，否则丢失格式
2. **`.doc` 格式读取** — python-docx 只支持 `.docx`。旧版 `.doc` 格式需用 `olefile` 库读取：先用 `olefile.OleFileIO()` 打开，读取 `WordDocument` 流，然后用 `utf-16-le` 解码提取中文文本。详见 `{baseDir}/references/读取doc文件.md`
3. **页眉页码** — 需要用域代码（PAGE field），不能硬编码页码
4. **图片占位符** — 单独处理，先清空文本再插入图片
5. **中文字体** — 必须设置 `run.font.element.rPr` 的 `w:eastAsia` 属性
6. **表格合并单元格** — python-docx 处理合并单元格较复杂，替换时需检查 cell 是否被合并
7. **采集表字数限制** — 部分字段有50字限制，大模型生成时需控制长度
8. **交互循环** — 采集表需要多轮交互，直到用户确认；说明书用户只审阅大纲
9. **分步生成** — 说明书按章节生成，每章自动审阅后再继续，避免前后矛盾
10. **上下文传递** — 每章生成时传入前几章摘要，保持一致性
11. **存档机制** — 每步结果保存到JSON，中断后可续写
12. **主要功能描述** — 用户要求详细丰富（100-200字），按功能模块分点描述，不能过于简略
13. **信息采集表填写要求** — 详见 `{baseDir}/references/信息采集表填写要求.md`，包含字数限制、必填/选填规则
14. **⚠️ Word格式** — 必须严格按照 `{baseDir}/references/格式规范.md` 的格式生成文档。关键：一级标题和二级标题都是黑体16pt**不加粗**，正文16pt Times New Roman首行缩进1.18cm两端对齐1.5倍行距段前段后0，图名14pt居中
15. **⚠️ 写作风格** — 必须按照 `{baseDir}/references/格式规范.md` 的风格写作，是用户操作指南不是技术文档！描述用户动作，不是系统功能
16. **⚠️ 每个功能必须有注意事项** — 用户明确要求每个功能模块都要有"注意事项"，提醒常见问题和操作要点
17. **⚠️ 必须有平台总体介绍章节** — 第一章必须是平台总体介绍，包含功能概述、总体架构、技术实现、数据流向，每个部分都需要配图
18. **⚠️ 代码文档按65页提取** — 考虑封面页等额外页数，代码文档按65页（3250行）提取，生成后用脚本检查总行数是否足够
19. **⚠️ 排除第三方库** — 代码文档提取时排除 `node_modules/`、`.venv/`、`__pycache__/`、`dist/` 等目录
20. **JSON中的中文引号** — 生成包含中文内容的JSON时，避免使用「」「」等中文引号，会导致Python `json.loads` 解析失败。改用【】或省略引号
21. **项目分析要点** — Vue.js项目重点看：`router/index.ts`（路由→功能模块）、`views/*.vue`（页面→具体功能）、`backend/src/services/`（后端→业务逻辑）、`README.md`（官方功能描述）。从这4个来源交叉验证，生成功能描述
22. **⚠️ 提交前检查清单** — 生成文档后必须检查：字号是否正确（封面22pt，标题16pt，正文16pt，图名14pt）、是否有功能表格、图片标题与实际图片是否匹配、文档字数是否满足页数要求、信息采集表必填字段是否完整
23. **⚠️ 截图补充说明** — 生成的文档中图片标题是占位符，用户需要手动补充系统截图。在提交清单中明确标注哪些图片需要补充
24. **⚠️ 配图生成** — **必须使用Excalidraw Diagram Skill**。工作流程：加载skill → 手写Excalidraw JSON → `render_excalidraw.py` 渲染PNG → 视觉验证循环2-4次 → `replace_docx_images.py` 插入Word。不要用Python脚本生成JSON，不要用Mermaid，不要用matplotlib作为最终方案。详见配图生成流程章节
25. **⚠️ docx图片替换** — 替换已生成docx中的图片时，使用zipfile解压→替换word/media/下的文件→重新打包。**不要创建.backup文件**，否则会被打包进docx导致文件大小翻倍。替换完成后清理临时目录。详见 `{baseDir}/references/配图生成最佳实践.md`
26. **⚠️ 中文字体优先级** — WSL环境下优先使用 `WenQuanYi Zen Hei`（系统自带），其次才是 `SimHei`（可能未安装）
27. **⚠️ 截图功能** — 软著说明书需要大量系统截图，提供两种模式：
    - **模式B：智能匹配**（推荐）：用户预先截图放到文件夹，用视觉模型分析截图内容，根据功能描述自动匹配到说明书章节。使用 `{baseDir}/scripts/match_screenshots.py`
    - **模式A：自动截图**：给系统URL，用Playwright自动访问并截图。使用 `{baseDir}/scripts/auto_screenshot.py`
    - 详见 `{baseDir}/references/截图功能规范.md`
28. **⚠️ 截图命名规范** — 截图文件建议使用数字前缀+功能名称的格式（如 `01_登录页面.png`），方便匹配和排序
29. **⚠️ 截图质量要求** — 系统截图分辨率建议1920x1080或更高，避免截取浏览器边框，确保页面内容清晰可读
30. **⚠️ 国内环境** — pip安装使用清华镜像：`pip install xxx -i https://pypi.tuna.tsinghua.edu.cn/simple`；npm使用淘宝镜像：`npm config set registry https://registry.npmmirror.com`

## 提示词模板

本skill在 `{baseDir}/prompts/` 目录下提供了结构化的提示词模板，供Agent在各阶段参考：

- `{baseDir}/prompts/大纲生成.md` — 大纲生成提示词
- `{baseDir}/prompts/章节生成.md` — 章节生成提示词（含JSON输出格式和示例）
- `{baseDir}/prompts/章节审阅.md` — 章节审阅提示词
- `{baseDir}/prompts/代码提取.md` — 代码提取提示词

## 参考文档

- `{baseDir}/references/格式规范.md` — Word格式 + 写作规范完整版
- `{baseDir}/references/信息采集表填写要求.md` — 各字段填写要求和字数限制
- `{baseDir}/references/常见问题.md` — 实际使用中的问题和解决方案
- `{baseDir}/references/软著申请要求.md` — 软著申请的总体要求
- `{baseDir}/references/提交清单模板.md` — 提交清单模板
- `{baseDir}/references/配图生成最佳实践.md` — 配图方案选择和最佳实践
- `{baseDir}/references/图表工具调研报告.md` — 图表工具对比调研
- `{baseDir}/references/截图功能规范.md` — 截图功能使用流程
- `{baseDir}/references/截图功能使用示例.md` — 截图功能完整示例
- `{baseDir}/references/文档验证脚本.md` — 文档格式验证脚本
- `{baseDir}/references/章节生成提示词.md` — 章节生成的提示词模板
- `{baseDir}/references/读取doc文件.md` — 读取旧版.doc格式文件的方法
- `{baseDir}/references/python-docx操作要点.md` — python-docx库使用要点
- `{baseDir}/references/多前端项目分析策略.md` — 多前端项目的识别和分析策略
- `{baseDir}/references/项目分析扫描清单.md` — 项目分析的扫描清单
