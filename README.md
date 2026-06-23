# 📋 软件著作权文档生成 Skill

> AI Agent 驱动的中国软著申请文档自动生成工具。分析项目代码，自动生成信息采集表、使用说明书和源代码文档。

## ✨ 功能特性

- 🔍 **智能扫描** — 自动识别项目技术栈、功能模块、业务逻辑
- 📝 **采集表生成** — 交互式确认信息，自动填充Word模板
- 📖 **说明书撰写** — 分章节生成用户操作指南风格的说明书
- 💻 **代码提取** — 按优先级提取核心代码，生成前30页+后30页
- 🎯 **格式合规** — 严格遵循版权中心的字号、字体、排版要求

## 🚀 快速开始

### 安装

```bash
# 通用安装（支持所有主流AI Agent）
npx skills add Foamtor/software-copyright-skill

# OpenClaw（龙虾）用户
openclaw skills install Foamtor/software-copyright-skill
```

### 安装Python依赖

```bash
pip install python-docx lxml Pillow olefile
```

### 使用

在你的AI Agent中输入：

```
帮我为当前项目生成软著文档
```

Agent会自动：
1. 扫描项目结构
2. 确认软件信息
3. 生成使用说明书大纲
4. 分章节撰写内容
5. 提取源代码文档
6. 输出三份Word文档

## 🤖 支持的AI Agent

| Agent | 安装方式 | 状态 |
|-------|---------|------|
| [Hermes Agent](https://hermes-agent.nousresearch.com) | `npx skills add` | ✅ |
| [Claude Code](https://docs.anthropic.com/claude-code) | `npx skills add` | ✅ |
| [Cursor](https://cursor.sh) | `npx skills add` | ✅ |
| [Codex CLI](https://github.com/openai/codex) | `npx skills add` | ✅ |
| [OpenClaw（龙虾）](https://openclaw.ai) | `openclaw skills install` | ✅ |

所有平台使用同一个 `SKILL.md` 文件，遵循 [AgentSkills](https://github.com/vercel-labs/skills) 规范。

## 📁 生成文档说明

### 信息采集表
- 软件基本信息（名称、版本号、开发方式等）
- 开发与运行环境（硬件、操作系统、编程语言等)
- 功能特点描述（每项50字以内）

### 使用说明书
- 用户操作指南风格（不是技术文档）
- 按功能模块组织，含截图占位
- 每页≥30行，前30页+后30页
- 第一章必须是平台总体介绍

### 源代码文档
- 按优先级提取：主入口→路由→核心→公共→API→工具
- 每页≥50行，前30页+后30页
- 自动排除第三方库和构建产物

## 🔧 独立使用（不通过Agent）

```bash
# 扫描项目
python3 scripts/scan_project.py --path ./my-project --output ./output/project_info.json

# 填充信息采集表
python3 scripts/fill_template.py \
  --template templates/信息采集表模板.docx \
  --content ./output/采集表内容.json \
  --output ./output/信息采集表.docx

# 生成说明书章节
python3 scripts/generate_manual.py \
  --content ./output/第1章内容.json \
  --output ./output/说明书_第1章.docx

# 生成代码文档
python3 scripts/generate_code_doc.py \
  --project ./my-project \
  --files ./output/文件列表.json \
  --output ./output/代码文档.docx \
  --software-name "我的系统V1.0" \
  --version "V1.0"

# 合并章节
python3 scripts/merge_chapters.py \
  --chapters ./output/说明书_第*.docx \
  --output ./output/使用说明书.docx \
  --software-name "我的系统V1.0" \
  --version "V1.0"
```

## 📚 参考文档

- [格式规范](references/格式规范.md) — Word排版格式 + 写作风格要求
- [信息采集表填写要求](references/信息采集表填写要求.md) — 各字段字数限制和填写规范
- [常见问题](references/常见问题.md) — 实际使用中的问题和解决方案

## 📄 许可证

[MIT License](LICENSE)

## 🙏 致谢

- [python-docx](https://github.com/python-openxml/python-docx) — Word文档操作
- [AgentSkills](https://github.com/vercel-labs/skills) — 统一的AI Agent Skill标准
