# 阶段1：项目分析

## 目标

分析项目代码，理解软件功能、技术栈、业务逻辑。

## 流程

### 1. 扫描项目结构

```bash
python3 scripts/scan_project.py --path /project --output /tmp/project_info.json
```

### 2. 识别前端项目

**重要**：现代项目可能有多个前端目录：
- `ui_desgin/` — 功能设计原型（功能模块以此为准）
- `agent_app/` — 移动端APP代码（技术架构以此为准）
- `agent_ui/` — Web端代码

**必须向用户确认**：「项目有多个前端目录，请确认功能模块以哪个为准？」

### 3. 阅读关键文件

| 文件类型 | 作用 | 重点关注 |
|----------|------|----------|
| README.md | 官方功能描述 | 软件定位、核心功能 |
| router/*.ts | 路由定义 | 功能模块列表 |
| views/*.vue | 页面组件 | 具体功能实现 |
| package.json | 依赖信息 | 技术栈 |
| main.ts | 入口文件 | 系统架构 |

### 4. 交叉验证

从4个来源交叉验证功能描述：
1. UI设计稿 → 功能模块定义
2. APP源码 → 技术架构实现
3. 后端API → 业务逻辑
4. README → 官方描述

## 输出

```json
{
  "name": "农村宅基地管理信息系统",
  "version": "V1.0",
  "tech_stack": ["Vue.js", "FastAPI", "PostgreSQL"],
  "modules": [
    {"name": "农户端", "features": ["建房申请", "办件跟踪"]},
    {"name": "管理端", "features": ["审批管理", "统计分析"]}
  ],
  "entry_points": ["main.ts", "router/index.ts"]
}
```

## 注意事项

1. **不要混淆三个代码库** — ui_desgin是功能定义，agent_app是技术实现
2. **功能以UI设计稿为准** — APP代码只提供技术架构参考
3. **用户纠正信号要重视** — "前端是app，功能设计目录在xxx"是明确指令
4. **排除第三方库** — 扫描时排除 node_modules/、.venv/、__pycache__/ 等
