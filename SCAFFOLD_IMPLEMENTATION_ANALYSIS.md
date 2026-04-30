# AI Engineering Scaffold (AIES) - 脚手架完整实现分析

生成时间：2026-04-30

---

## 📋 总览

**AIES（AI Engineering Scaffold）** 是一套用于初始化「全 AI 开发工程」的脚手架，具备以下特点：

### 🎯 核心能力
1. **像老员工一样做事** —— 自动加载项目规范、理解架构、遵循代码风格
2. **跨会话不失忆** —— 用结构化日志持久化每次会话的关键决策与上下文
3. **被标准化验收** —— 所有产出都要过「任务启动清单 → 质量自检 → 索引更新」三关
4. **多 Agent 协作** —— 复杂任务可拆解为 plan → implement → check → debug 流水线
5. **一次写规范，全平台生效** —— 同一份 `spec/` 被 Claude Code / Cursor / CodeBuddy / Copilot / Codex 共享

### 🔄 工作模式
- **Phase 1**：任务启动清单（写代码前第一段输出）
- **Phase 2**：执行（按清单读取 → 生成代码）
- **Phase 3**：任务完成清单（质量自检 → 索引更新 → 建议 commit）
- **Phase 4**：会话日志（记录决策与文件变更）

---

## 📂 完整目录树

```
ai-engineering-scaffold/
├── README.md                           # 项目介绍
├── bootstrap.py                        # 一键初始化脚本（核心工具）
├── bootstrap.sh                        # Shell 版本
├── .gitignore                          # Git 忽略规则
│
├── .ai/                                # AI 协作工作区
│   ├── index.md                        # 项目地图/索引
│   ├── changelog.md                    # 变更日志
│   ├── context-guide.md                # 场景上下文指南
│   ├── glossary.md                     # 业务术语表
│   ├── known-issues.md                 # 已知技术债
│   ├── review-checklist.md             # AI 代码审查清单
│   └── prompts/                        # Prompt 模板库
│       ├── README.md
│       ├── new-feature.md
│       ├── fix-bug.md
│       ├── code-review.md
│       ├── git-commit.md
│       └── refactor.md
│
├── .aies/                              # 工作流与规范体系
│   ├── config.yaml                     # 全局配置
│   ├── workflow.md                     # 标准工作流（必读）
│   ├── spec/                           # 分层规范库
│   │   ├── index.md                    # 规范导航
│   │   ├── architecture.md             # 架构规范
│   │   ├── code-style.md               # 代码风格规范
│   │   ├── error-handling.md           # 错误处理规范
│   │   ├── logging.md                  # 日志规范
│   │   ├── quality-gates.md            # 质量门规范
│   │   └── testing.md                  # 测试规范
│   ├── tasks/                          # 任务管理
│   │   └── {MM-DD-slug}/
│   │       ├── task.json
│   │       ├── prd.md
│   │       └── acceptance.md
│   ├── workspace/                      # 会话日志存储
│   │   └── {developer}/
│   │       ├── index.md
│   │       ├── journal-1.md
│   │       └── ...
│   └── scripts/                        # Python 工具脚本
│       ├── session.py
│       ├── task.py
│       ├── init-developer.py
│       └── lib/common.py
│
├── platforms/                          # 多平台适配
│   ├── claude/                         # Claude Code
│   │   ├── CLAUDE.md                   # 规范入口
│   │   ├── settings.json               # 配置
│   │   ├── hooks/session-start.py      # Hook
│   │   ├── commands/                   # Slash 命令
│   │   └── agents/                     # 多 Agent 定义
│   ├── cursor/                         # Cursor IDE
│   ├── codebuddy/                      # CodeBuddy
│   ├── copilot/                        # GitHub Copilot
│   ├── codex/                          # 其他平台
│   └── common/                         # 通用规范
│
├── docs/                               # 设计文档
│   ├── philosophy.md                   # 全 AI 开发哲学
│   ├── multi-agent-decision.md         # 何时需要多 Agent
│   ├── migration-guide.md              # 迁移指南
│   └── agent-manage-backend-review.md  # 真实案例复盘
│
├── ci/                                 # 质量门
│   ├── github-actions/ai-review.yml
│   └── pre-commit/ai-review-hook.sh
│
└── examples/                           # 示例项目
    └── README.md
```

---

## 🔑 核心文件详解

### 1️⃣ bootstrap.py（初始化脚本）

**作用**：一键将 AIES 脚手架复制到新项目

**三种使用方式**：
```bash
# 交互式（推荐）
python3 bootstrap.py --interactive

# 指定参数
python3 bootstrap.py --target /path/to/project --developer your-name \
    --platforms claude,cursor,codebuddy --mode merge

# 最简（当前目录）
python3 bootstrap.py --here --developer your-name
```

**支持三种模式**：
- `fresh` —— 全新项目，直接拷贝
- `merge` —— 已有项目，保留已有文件（推荐）
- `add` —— 仅添加缺失文件，不覆盖任何已有文件

**核心功能**：
- 拷贝核心目录（`.ai/`、`.aies/`）
- 拷贝平台适配文件（Claude、Cursor、CodeBuddy 等）
- 更新 `.gitignore`
- 替换模板占位符（PROJECT_NAME、LAST_UPDATED 等）
- 初始化开发者身份

---

### 2️⃣ .aies/workflow.md（工作流规范）

**4 个阶段工作流**：

#### Phase 0：会话初始化
```bash
python3 .aies/scripts/init-developer.py your-name
python3 .aies/scripts/session.py get-context
```

#### Phase 1：任务启动清单（写代码前必须）
```
📋 任务启动清单
━━━━━━━━━━━━━━
• 任务类型：[新增/修改/修复/重构/其他]
• 绑定任务：[task.json title，或 "即时任务"]
• 需读取的参考文件：[按 .ai/context-guide.md 列出]
• 涉及的规范要点：[从 .aies/spec/ 列出相关强制项]
• 预计变更文件：[将要修改/新增的文件]
• 索引需更新：[是/否]
```

#### Phase 2：执行
- 读取参考文件
- 按 `.aies/spec/` 规范生成代码
- 主动指出潜在风险
- 关键决策处补充注释

#### Phase 3：任务完成清单（写完代码后必须）
```
✅ 任务完成清单
━━━━━━━━━━━━━━
1. 质量自检（参照 .ai/review-checklist.md）
2. 测试验收（参照 acceptance.md）
3. 索引更新：[已更新 .ai/index.md / 无需更新]
4. 建议 commit message：`type(scope): 描述 [ai-assisted]`
5. 会话日志建议：python3 .aies/scripts/session.py add ...
6. Spec 缺口沉淀：[是否发现新约定需要沉淀到 .aies/spec/]
```

#### Phase 4：会话结束
```bash
python3 .aies/scripts/session.py add \
    --title "本次会话标题" \
    --commit "$(git rev-parse --short HEAD)" \
    --summary "变更摘要"
```

---

### 3️⃣ .aies/spec/ 规范库

#### 📄 architecture.md（架构规范）
- **分层架构**：入口层 → 业务层 → 数据层
- **依赖方向**：严格单向，禁止逆向依赖
- **上下文透传**：所有跨层调用必须透传 context
- **单一职责**：每个函数/类只做一件事
- **开闭原则**：对扩展开放，对修改关闭
- **显式优于隐式**：错误必须显式处理

#### 📄 code-style.md（代码风格）

**命名规范**：
- 常量：`UPPER_SNAKE_CASE`
- 变量/函数：按语言约定（camelCase）
- 类/结构体：`PascalCase`
- 文件：按语言约定（Go: snake_case，TS: kebab-case）

**注释强制**：
- 结构体字段：含义 + 枚举值 + 默认值 + 约束
- 函数注释：参数、返回值、错误类型
- 复杂逻辑：决策注释（为什么这样做）

**禁止模式**：
- ❌ 魔法数字
- ❌ 静默吞掉错误
- ❌ 拼接字符串构造 SQL
- ❌ 硬编码敏感信息

**必须模式**：
- ✅ Update DTO 用指针类型（区分「不传」和「传 null」）
- ✅ 错误使用项目统一错误码
- ✅ 日志使用结构化字段
- ✅ 时间字段统一 UTC

#### 📄 error-handling.md（错误处理）

**错误分类**：
- 参数错误 (400)
- 未授权 (401)
- 无权限 (403)
- 资源不存在 (404)
- 冲突 (409)
- 限流 (429)
- 服务器错误 (500)

**必须模式**：
- ✅ 错误立即记日志
- ✅ 错误信息不暴露内部细节
- ✅ 使用项目统一错误类型
- ✅ 错误包装保留原始信息

**禁止模式**：
- ❌ 静默吞错误
- ❌ panic 代替 error
- ❌ 混合多种错误风格

#### 📄 logging.md（日志规范）

**日志级别**：
- `debug` —— 开发调试信息
- `info` —— 正常业务流程关键节点
- `warn` —— 非预期但不影响功能
- `error` —— 需要人工关注的错误
- `fatal` —— 不可恢复错误

**必须字段**：
- `time` —— 时间戳（UTC ISO 8601）
- `level` —— 日志级别
- `msg` —— 日志消息
- `trace_id` —— 链路追踪 ID
- `user_id` —— 当前用户 ID

**禁止字段**：
- 密码、密钥、token、cookie
- 身份证、银行卡、手机号
- 个人隐私、内部 SQL、堆栈

#### 📄 quality-gates.md（质量门）

**提交前必过**：
- [ ] 编译/类型检查通过
- [ ] Lint/格式化通过
- [ ] 相关单元测试通过
- [ ] API 文档已更新
- [ ] `.ai/index.md` 已更新

**禁止合并**：
- ❌ 编译/类型/lint 不通过
- ❌ 跳过 Hooks 提交
- ❌ 包含临时标记（TODO: fixme before merge）
- ❌ AI 生成代码未标注 `[ai-assisted]`

#### 📄 testing.md（测试规范）

**强制**：每个任务必须有 `acceptance.md`（验收与测试文件）

**三层覆盖**：
1. **单元测试**：验证单个函数的行为
   - 外部依赖全部 Mock
   - 覆盖正常路径 + 异常 + 边界
2. **集成测试**：验证模块间接口契约
3. **E2E 测试**：验证完整功能链路

**Mock 规范**：
- LLM Mock
- 文件 IO Mock
- 外部 HTTP Mock

**测试文件位置**：
```
{project}/tests/
├── unit/test_{module}.py
├── integration/test_{subgraph}.py
└── e2e/test_{feature}.py
```

---

### 4️⃣ platforms/claude/CLAUDE.md（Claude Code 规范入口）

**必读文件**（每次会话开始）：
1. `.aies/workflow.md` —— 工作流（Phase 1/2/3 协议）
2. `.aies/spec/index.md` —— 规范导航
3. `.ai/index.md` —— 项目地图
4. `.ai/review-checklist.md` —— 审查清单

**Slash 命令**：
| 命令 | 作用 |
|------|------|
| `/aies:start` | 初始化会话 |
| `/aies:finish-work` | 完成清单 |
| `/aies:new-feature` | 按模板执行 |
| `/aies:fix-bug` | 按模板执行 |
| `/aies:review` | 按模板执行 |
| `/aies:commit` | 按模板执行 |

---

### 5️⃣ .aies/config.yaml（全局配置）

```yaml
# 会话日志
max_journal_lines: 2000              # 单文件最大行数
session_commit_message: "chore: record session journal"
auto_commit_journal: false           # 自动提交日志变更

# 任务生命周期 Hooks
hooks: {}

# 多开发者支持
require_developer_init: true
developer_file: ".aies/.developer"

# 平台适配
platforms:
  - claude
  - cursor
  - codebuddy
  - universal

# 多 Agent 流水线
multi_agent:
  enabled: false
```

---

### 6️⃣ 任务管理系统

**任务目录结构**：
```
.aies/tasks/{MM-DD-slug}/
├── task.json
├── prd.md              # 需求描述
└── acceptance.md       # 验收与测试（强制）
```

**任务命令**：
```bash
# 创建任务
python3 .aies/scripts/task.py create "任务标题" --slug task-slug

# 查看任务
python3 .aies/scripts/task.py list           # 活跃任务
python3 .aies/scripts/task.py list-archive   # 已归档任务

# 归档任务
python3 .aies/scripts/task.py archive task-slug
```

**⚠️ 强制**：`acceptance.md` 必须在 implement 阶段开始前填写完毕。

---

### 7️⃣ 会话日志系统

**日志存储**：
```
.aies/workspace/{developer}/
├── index.md              # 个人索引（自动维护）
├── journal-1.md          # 日志文件（≤ 2000 行）
├── journal-2.md          # 超过 2000 行自动切换
└── ...
```

**日志条目格式**：
```markdown
## [时间戳] 会话标题

**Commit**: abc1234
**摘要**: ...

### 关键决策
- ...

### 变更文件
- ...
```

---

## 🏗️ 架构设计原则

### 1. Spec 在仓库，生效在平台
- 规范只写一份（`.aies/spec/`、`.ai/`）
- 各平台通过入口文件引用，不做重复

### 2. 渐进式上下文
- `index.md` 作为导航
- AI 按需读取具体章节
- 不一次性灌满上下文

### 3. 默认单 Agent，按需多 Agent
- 绝大多数场景单 Agent + Spec + 清单就够用
- 多 Agent 仅用于长耗时/高复杂度任务

### 4. 人是质量门最后一道
- AI 自检只是第一道
- `review-checklist.md` 必须由人过一遍

### 5. 方法论 > 工具
- 脚手架是方法论的载体
- 必须先读 `docs/philosophy.md`

---

## 📚 使用流程

### 初始化一个新项目

```bash
# 步骤 1：进入新项目目录
cd /path/to/your-new-project

# 步骤 2：运行初始化脚本
python3 /path/to/ai-engineering-scaffold/bootstrap.py --interactive

# 步骤 3：根据提示选择
# - 语言栈（Go / TypeScript / Python 等）
# - AI 平台（Claude Code / Cursor 等）
# - 启用多 Agent 流水线
# - 启用 Git Hooks

# 步骤 4：编辑项目规范
cat .aies/spec/index.md           # 规范导航
cat .aies/spec/architecture.md    # 架构约束
cat .ai/index.md                  # 项目地图
```

### 每次开发任务流程

```bash
# 步骤 1：初始化会话上下文
python3 .aies/scripts/session.py get-context

# 步骤 2：创建任务（可选）
python3 .aies/scripts/task.py create "功能标题" --slug feature-slug

# 步骤 3：AI 输出 Phase 1 清单
# - 读规范
# - 读索引
# - 读参考文件

# 步骤 4：AI 执行（Phase 2）
# - 按规范生成代码
# - 指出风险
# - 补充决策注释

# 步骤 5：AI 输出 Phase 3 完成清单
# - 质量自检
# - 测试验收
# - 索引更新
# - Spec 缺口

# 步骤 6：记录会话日志
python3 .aies/scripts/session.py add \
    --title "功能开发完成" \
    --commit "$(git rev-parse --short HEAD)" \
    --summary "添加了 X 功能，改了 Y 文件，关键决策是..."
```

---

## ✅ 禁止事项

- ❌ 跳过 Phase 1 清单直接写代码
- ❌ 完成后不更新 `.ai/index.md`
- ❌ 大段重写用户未要求的代码
- ❌ 生成代码时编造项目中不存在的函数/类型
- ❌ 日志日期混乱、多个 journal 并行追加
- ❌ `git commit`/`git push` 未经用户确认
- ❌ 没有 `acceptance.md` 就开始 implement
- ❌ 测试文件里发真实网络请求

---

## 🎓 推荐阅读顺序

1. `docs/philosophy.md` —— 全 AI 开发哲学（必读）
2. `docs/multi-agent-decision.md` —— 何时需要多 Agent
3. `docs/migration-guide.md` —— 迁移指南
4. `docs/agent-manage-backend-review.md` —— 真实案例复盘
5. `.aies/workflow.md` —— 工作流规范
6. `.aies/spec/index.md` —— 规范导航

---

## 📊 快速对比：AIES vs 传统工程

| 维度 | 传统工程 | AIES |
|-----|---------|------|
| 规范管理 | 分散、人脑记忆 | 集中、结构化 Spec |
| AI 上下文 | 每次重新灌入 | 结构化索引、会话日志复用 |
| 代码质量 | 人工审查 | AI 自检 + 人工最后一道 |
| 多 Agent | 无 | plan → implement → check → debug |
| 跨会话 | 失忆 | 完整日志追踪 |
| 平台支持 | N/A | 一份规范，多平台生效 |

---

## 🔗 文件关系图

```
项目根目录
│
├─ .ai/                          # AI 协作工作区
│  ├─ index.md                   # ← 每次读取（项目地图）
│  ├─ review-checklist.md        # ← Phase 3 自检
│  ├─ context-guide.md           # ← Phase 1 参考文件选择
│  └─ changelog.md               # ← 沉淀新约定
│
├─ .aies/                        # 工作流与规范体系
│  ├─ workflow.md                # ← 必读（4 阶段协议）
│  ├─ spec/
│  │  ├─ index.md                # ← 规范导航
│  │  ├─ architecture.md         # ← 架构约束
│  │  ├─ code-style.md           # ← 代码风格
│  │  ├─ error-handling.md       # ← 错误处理
│  │  ├─ logging.md              # ← 日志规范
│  │  ├─ quality-gates.md        # ← 质量门
│  │  └─ testing.md              # ← 测试规范
│  ├─ tasks/
│  │  └─ {slug}/
│  │     ├─ task.json
│  │     ├─ prd.md
│  │     └─ acceptance.md        # ← 强制
│  ├─ workspace/
│  │  └─ {developer}/
│  │     └─ journal-N.md         # ← 会话日志
│  └─ scripts/
│     ├─ session.py
│     ├─ task.py
│     └─ init-developer.py
│
├─ platforms/                    # 多平台适配
│  ├─ claude/
│  │  ├─ CLAUDE.md               # ← Claude 入口
│  │  └─ agents/                 # ← 多 Agent 定义
│  ├─ cursor/
│  ├─ codebuddy/
│  └─ ...
│
└─ docs/                         # 设计文档
   ├─ philosophy.md              # ← 必读（理论基础）
   └─ ...
```

---

**生成完毕！** 这份总结涵盖了 AIES 脚手架的完整实现细节。
