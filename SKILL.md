---
name: software-copyright-skill
description: 生成中国软件著作权（软著）登记申请文档。分析项目代码，自动生成信息采集表、使用说明书和源代码文档。适用于各类AI Agent。
metadata:
  author: Foamtor
  version: 1.0.0
  homepage: https://github.com/Foamtor/software-copyright-skill
license: MIT
---

# 软著文档生成 Skill

核心原则：**AI Agent负责理解和生成内容，Python脚本负责文件IO和格式操作。**

## 前置依赖

```bash
pip install python-docx lxml Pillow olefile
```

## 工作流程概览

```
阶段1: 扫描项目 → 阶段2: 确认信息 → 阶段3: 生成大纲
→ 阶段4: 分章撰写 → 阶段5: 代码提取 → 阶段6: 合并输出
```

## 三份文档规格

| 文档 | 页数要求 | 核心内容 |
|------|---------|---------|
| 信息采集表 | 2页 | 软件基本信息 + 开发运行环境 |
| 使用说明书 | 前30页+后30页，每页≥30行 | 用户操作指南风格，含截图 |
| 源代码文档 | 前30页+后30页，每页≥50行 | 主入口→路由→核心→公共→API→工具 |

## 阶段1：扫描项目

调用扫描脚本获取项目结构：

```bash
python3 {baseDir}/scripts/scan_project.py --path /项目路径 --output /tmp/project_info.json
```

读取关键文件（README、package.json、路由、主入口），理解：
- 软件名称、版本号
- 功能模块列表
- 技术栈
- 业务逻辑

**Vue.js项目重点看**：`router/index.ts`（路由→功能模块）、`views/*.vue`（页面→具体功能）、`backend/src/services/`（后端→业务逻辑）、`README.md`。

## 阶段2：交互式信息采集

向用户展示检测到的信息，请求确认：

```
| 字段 | 检测值 |
|------|--------|
| 软件全称 | xxx管理系统V1.0 |
| 编程语言 | Java、JavaScript |
| 主要功能 | 1.用户管理 2.数据查询 ... |
```

用户确认后，准备信息采集表数据（JSON格式），调用模板填充：

```bash
python3 {baseDir}/scripts/fill_template.py \
  --template {baseDir}/templates/信息采集表模板.docx \
  --content /tmp/采集表内容.json \
  --output /output/信息采集表.docx
```

**采集表字段字数限制**：功能特点每项50字以内。详见 `{baseDir}/references/信息采集表填写要求.md`。

## 阶段3：使用说明书大纲

生成三级目录大纲，交用户审阅：

```
一、平台总体介绍（必须有，第一章）
  （一）平台功能概述
  （二）总体架构
  （三）技术实现
  （四）数据流向
二、系统登录
  （一）登录入口
  （二）登录流程
三、xxx功能
  （一）xxx
    1. xxx
```

用户确认后进入分章生成。

## 阶段4：分章生成说明书

### 写作风格（必须遵守）

**软著说明书是用户操作指南，不是技术文档！**

正确写法：
```
在系统首页，点击"新建项目"按钮，弹出新建项目对话框。如下图。
图3 新建项目按钮
```

错误写法：
```
一、项目管理功能：支持创建和管理项目，实现数据治理工作的规范化管理。
```

### 写作要点
1. 面向用户操作：描述点击什么、填写什么、看到什么
2. 截图配文字：每段操作后跟"如下图。"，然后"图X xxx示意"
3. 每个功能必须有**注意事项**
4. 语言简洁，面向普通用户

### 分章生成流程

每章生成内容JSON后调用：

```bash
python3 {baseDir}/scripts/generate_manual.py \
  --content /tmp/第N章内容.json \
  --output /output/说明书_第N章.docx \
  --images-dir /output/images
```

JSON格式示例：
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

**上下文传递**：每章生成时传入前几章摘要，保持内容一致性。

## 阶段5：源代码文档

向用户确认提取文件列表后生成：

```bash
python3 {baseDir}/scripts/generate_code_doc.py \
  --project /项目路径 \
  --files /tmp/文件列表.json \
  --output /output/代码文档.docx \
  --software-name "XXX系统V1.0" \
  --version "V1.0"
```

提取顺序：主入口 → 路由 → 核心页面 → 公共组件 → API → 工具函数

**排除目录**：`node_modules/`、`.venv/`、`__pycache__/`、`dist/`、`build/`、`target/`

按65页提取（考虑封面等额外页数），每页≥50行。

## 阶段6：合并输出

```bash
python3 {baseDir}/scripts/merge_chapters.py \
  --chapters /output/说明书_第1章.docx /output/说明书_第2章.docx ... \
  --output /output/使用说明书.docx \
  --software-name "XXX系统V1.0" \
  --version "V1.0"
```

最终输出三份文档：
1. 信息采集表.docx
2. 使用说明书.docx
3. 代码文档.docx

## 格式规范速查

| 元素 | 格式 |
|------|------|
| 封面标题 | 22pt，黑体，加粗，居中 |
| 封面落款 | 16pt，宋体，加粗，居中 |
| 一级/二级标题 | 黑体，16pt，不加粗，首行缩进1.18cm |
| 正文 | Times New Roman + 宋体，16pt，首行缩进1.18cm，1.5倍行距 |
| 图名 | 14pt（4号字），居中 |
| 页眉 | 左：软件名称+版本号，右：页码 |

详细格式规范见 `{baseDir}/references/格式规范.md`。

## 配图方案

推荐方案（按优先级）：
1. **Excalidraw Diagram Skill** — 手绘风格，专业美观
2. **D2 Language** — 文本转图表，语法简洁
3. **matplotlib** — 基础方案，精确控制尺寸

不要使用Mermaid（字体太小，不适合打印）。

配图尺寸：宽10英寸，分辨率300dpi，中文字体用 WenQuanYi Zen Hei 或 SimHei。

## 截图补充

生成的文档中图片标题是占位符，用户需要手动补充系统截图：
- 截图分辨率建议1920×1080或更高
- 避免截取浏览器边框
- 文件命名：`01_登录页面.png`、`02_首页.png`

## ⚠️ 关键注意事项

1. **run级别替换** — 替换Word占位符时必须遍历 `para.runs`，不能用 `para.text =` 整体替换，否则丢失格式
2. **中文字体** — 必须设置 `run.font.element.rPr` 的 `w:eastAsia` 属性
3. **代码文档按65页提取** — 考虑封面等额外页数
4. **每章自动审阅** — 生成后检查内容一致性、准确性、完整性
5. **JSON中的中文引号** — 避免使用「」「」，改用【】或省略
6. **主要功能描述** — 用户要求详细丰富（100-200字），不能过于简略
7. **提交前检查** — 字号、功能表格、图片标题、页数、必填字段

## 参考文档

- `{baseDir}/references/格式规范.md` — Word格式 + 写作规范完整版
- `{baseDir}/references/信息采集表填写要求.md` — 各字段填写要求和字数限制
- `{baseDir}/references/常见问题.md` — 实际使用中的问题和解决方案
