# AI Engineering Scaffold

> **一套用于初始化「全 AI 开发工程」的脚手架**  
> 支持任何新工程零成本迁移，提供 AI 协作规范、任务管理、会话记忆、多 Agent 编排、CI 质量门等完整能力。

---

## 🎯 这是什么

`ai-engineering-scaffold`（简称 AIES）是一套**平台无关、语言无关**的 AI 工程化模板，核心目标是让 AI 在你的项目中：

1. **像老员工一样做事** —— 自动加载项目规范、理解架构、遵循代码风格
2. **跨会话不失忆** —— 用结构化日志持久化每次会话的关键决策与上下文
3. **被标准化验收** —— 所有产出都要过「任务启动清单 → 质量自检 → 索引更新」三关
4. **多 Agent 协作** —— 复杂任务可拆解为 plan → implement → check → debug 流水线
5. **一次写规范，全平台生效** —— 同一份 `spec/` 被 Claude Code / Cursor / CodeBuddy / Copilot / Codex 共享

---

## 📦 快速上手

### 方式 1：一键初始化新工程

```bash
# 从脚手架目录初始化目标工程
cd /path/to/ai-engineering-scaffold
python3 bootstrap.py --target /path/to/your-new-project --developer your-name

# 或者进入目标工程后执行
cd /path/to/your-new-project
python3 /path/to/ai-engineering-scaffold/bootstrap.py --developer your-name
```

### 方式 2：手动拷贝

```bash
cp -r ai-engineering-scaffold/.ai        your-project/
cp -r ai-engineering-scaffold/.aies      your-project/
cp    ai-engineering-scaffold/AGENTS.md  your-project/
cp    ai-engineering-scaffold/CLAUDE.md  your-project/
cp    ai-engineering-scaffold/.cursorrules your-project/  # 可选
```

### 方式 3：交互式按需选择（推荐）

```bash
cd /path/to/your-new-project
python3 /path/to/ai-engineering-scaffold/bootstrap.py --interactive
```

交互式引导你选择：
- 语言栈（Go / TypeScript / Python / Java / Rust / 其他）
- AI 平台（Claude Code / Cursor / CodeBuddy / Copilot / 全部）
- 启用多 Agent 流水线（是 / 否）
- 启用 Git Hooks（是 / 否）

---

## 📂 目录结构

```
ai-engineering-scaffold/
├── README.md                     ← 本文件
├── bootstrap.py                  ← 一键初始化脚本
├── bootstrap.sh                  ← Shell 版本（无 Python 环境时使用）
│
├── docs/                         ← 🧠 设计文档与方法论
│   ├── philosophy.md             ← 全 AI 开发环境构建哲学（必读）
│   ├── multi-agent-decision.md   ← 什么时候需要多 Agent（避免过度设计）
│   ├── migration-guide.md        ← 从现有工程迁移指南
│   └── agent-manage-backend-review.md  ← 以 agent-manage-backend 为例的得失复盘
│
├── .ai/                          ← 📋 AI 协作工作区（项目级、可提交）
│   ├── index.md                  ← 项目地图（架构/路由/模型/调用链）
│   ├── context-guide.md          ← 场景 → 需要提供的上下文文件
│   ├── review-checklist.md       ← AI 代码审查清单（8 维度）
│   ├── changelog.md              ← 变更日志（AI 自动追加）
│   ├── glossary.md               ← 业务术语表（统一 AI 和团队语义）
│   └── prompts/                  ← Prompt 模板库（按场景）
│       ├── new-feature.md
│       ├── fix-bug.md
│       ├── code-review.md
│       ├── git-commit.md
│       └── refactor.md
│
├── .aies/                        ← ⚙️ 任务管理与会话记忆（类 Trellis）
│   ├── workflow.md               ← 工作流说明（AI 必读）
│   ├── config.yaml               ← 配置（日志上限/Hooks）
│   ├── spec/                     ← 分层规范（语言/架构约定）
│   │   ├── index.md
│   │   ├── code-style.md
│   │   ├── architecture.md
│   │   ├── quality-gates.md
│   │   ├── error-handling.md
│   │   └── logging.md
│   ├── tasks/                    ← 任务目录（每任务一子目录）
│   │   └── .gitkeep
│   ├── workspace/                ← 会话日志（每开发者一目录）
│   │   └── .gitkeep
│   └── scripts/                  ← 辅助脚本（Python，可选 Node 版）
│       ├── session.py            ← get-context / add-session
│       ├── task.py               ← create / list / finish / archive
│       ├── init-developer.py
│       └── lib/
│           └── common.py
│
├── platforms/                    ← 🔌 各 AI 平台适配文件模板
│   ├── claude/
│   │   ├── CLAUDE.md
│   │   ├── commands/             ← /aies:start /aies:finish-work ...
│   │   ├── agents/               ← plan/implement/check/debug 子 Agent
│   │   ├── hooks/                ← session-start / inject-context
│   │   └── settings.json
│   ├── cursor/
│   │   ├── rules/
│   │   └── commands/
│   ├── codebuddy/
│   │   └── rules/
│   ├── copilot/
│   │   └── instructions/
│   ├── codex/
│   │   └── AGENTS.md
│   └── common/
│       └── AGENTS.md             ← 通用 Agent 入口
│
├── ci/                           ← 🛡️ CI 质量门（可选接入）
│   ├── github-actions/
│   │   └── ai-review.yml
│   └── pre-commit/
│       └── ai-review-hook.sh
│
└── examples/                     ← 📖 示例项目
    ├── go-gin/                   ← Go + Gin 四层架构模板
    ├── typescript-nest/          ← TypeScript + NestJS
    └── python-fastapi/           ← Python + FastAPI
```

---

## 🧭 核心设计原则（读懂后再用）

1. **Spec 在仓库，生效在平台** —— 规范只写一份（`.aies/spec/`、`.ai/`），各平台通过入口文件（`CLAUDE.md`/`AGENTS.md`/`.cursorrules` 等）引用，不做重复。
2. **渐进式上下文** —— `index.md` 作为导航，AI 按需读取具体章节，不一次性灌满。
3. **默认单 Agent，按需多 Agent** —— 绝大多数场景单 Agent + Spec + 清单就够用，多 Agent 仅用于长耗时/高复杂度任务（详见 `docs/multi-agent-decision.md`）。
4. **人是质量门最后一道** —— AI 自检只是第一道，`review-checklist.md` 必须由人过一遍。
5. **方法论 > 工具** —— 脚手架是方法论的载体，不是魔法盒子。请先读 `docs/philosophy.md`。

---

## 🚀 配套文档阅读顺序

1. `docs/philosophy.md` —— **必读**，了解构建理念
2. `docs/multi-agent-decision.md` —— 判断你的项目需不需要多 Agent
3. `docs/migration-guide.md` —— 将现有工程迁移到 AIES 的步骤
4. `docs/agent-manage-backend-review.md` —— 复盘一个真实案例的得失

---

## 📜 License

本脚手架基于 MIT License 开放，fork 自用无需署名，但欢迎回馈改进。
