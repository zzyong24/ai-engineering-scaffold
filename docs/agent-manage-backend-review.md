# 案例复盘：agent-manage-backend 的全 AI 开发实践

> 本文基于对某 Go + Gin 智能体管理后端工程的深入分析，评估其 AI 工程化建设的成熟度、亮点、不足，并给出迁移到 AIES 脚手架的建议。

---

## 一、现状摘要（截至 2026-04-24）

`agent-manage-backend` 是一个 Go + Gin + GORM 的后端服务（智能体管理平台），约 40 个 Go 文件，263 个文件。AI 工程化设施横跨 6 套体系：

| 体系 | 位置 | 作用 |
|------|------|------|
| `.ai/` | `.ai/index.md`、`.ai/prompts/`、`.ai/review-checklist.md` | 项目级 AI 工作区（索引/模板/审查清单） |
| `.codebuddy/` | `rules/`、`memory/`、`skills/` | CodeBuddy IDE 的规则+记忆+技能 |
| `.claude/` | `agents/`、`commands/`、`hooks/`、`settings.json` | Claude Code 的多 Agent 流水线 |
| `.cursor/` | `commands/`、`rules/` | Cursor 的自定义命令 |
| `.trellis/` | `spec/`、`tasks/`、`scripts/`、`workflow.md` | Trellis 任务管理与会话记忆 |
| 根目录入口 | `CLAUDE.md`、`AGENTS.md`、`Rule.md` | 各平台入口文件 |

**整体评价**：**成熟度 4.5/5**（罕见的深度实践案例），但也存在可优化空间。

---

## 二、做得好的地方（强烈推荐迁移保留）⭐

### ⭐ 1. 规范细致到"AI 可执行"级别（维度 1 + 维度 3 典范）

`.codebuddy/rules/ai-collaborative-development.md` 写得极其到位，核心优点：

#### ✅ 亮点 A：每条规则都是"可执行的约束"

```markdown
❌ 抽象："请遵守 SOLID 原则"
✅ 可执行："函数参数数量不超过 4 个且第 1 个参数必须为 ctx context.Context"
✅ 可执行："禁止 fmt.Errorf()，必须使用 errno 包"
✅ 可执行："Model 层 function 必须使用指针接收器"
```

#### ✅ 亮点 B：强制执行协议（Phase 1/2/3）

```
收到任务 → 【Phase 1: 启动清单】→ 【Phase 2: 执行】→ 【Phase 3: 完成清单】
             ↓ 必须输出                              ↓ 必须输出
         「📋 任务启动清单」                     「✅ 任务完成清单」
```

这个"结构化输出"机制是**防止 AI 跳过规则**的关键，比单纯的"alwaysApply: true"强得多，因为输出可验证。

#### ✅ 亮点 C：具体反例驱动

几乎每条规则都给了 ✅ 正确写法 + ❌ 错误写法的代码对比，AI 不会歧义。

**建议**：AIES 脚手架**完整继承**这个规范体系，作为默认 Spec 模板。

---

### ⭐ 2. .ai/index.md 项目地图堪称典范

这是我见过最好的项目索引文件之一，包含 4 大块：

1. **目录结构总览**（每个文件职责说明）
2. **API 路由表**（35+ 端点按通道分组，带 Handler 和说明）
3. **数据模型关系**（ER 图 + 6 张表约束说明）
4. **模块调用关系**（从 main.go 到各层的完整调用链）

**价值**：
- 新 AI 会话读完这份文件，5 分钟内就能理解整个系统
- 索引和 changelog 分离，避免每次读 index 都把历史变更带进来（省 token）
- 维护规则明确（"每次新增/修改/删除文件后，必须同步更新"）

**建议**：AIES 脚手架模板化这个结构。

---

### ⭐ 3. Spec 分层设计（Trellis spec/backend/）

`.trellis/spec/backend/` 按领域分为 6 个子文件：

```
spec/backend/
├── index.md                   ← 导航 + 开发前必读清单
├── directory-structure.md     ← 目录结构 + 四层职责
├── database-guidelines.md     ← GORM 操作规范
├── error-handling.md          ← errno 包规范
├── logging-guidelines.md      ← Zap 结构化日志
├── quality-guidelines.md      ← 禁止模式 + 必须模式
└── skill-security-scan.md     ← Skill 安全扫描技能
```

**做得好的点**：
- **index.md 作为导航**，AI 按任务类型选择性读取 → 符合"最小充分上下文"
- 每份 spec 都有"任务启动清单"和"任务完成清单"
- Zip Slip 等安全问题有专门章节，避免 AI 盲区

**建议**：AIES 保留这种分层结构，但**统一到 `.aies/spec/` 单一位置**（避免 `.ai/` 和 `.trellis/spec/` 双头维护）。

---

### ⭐ 4. Prompt 模板库的实战性

`.ai/prompts/` 下 5 个模板（new-api.md / fix-bug.md / code-review.md / git-commit.md / build-image.md）的特点：

- **模板本身就是可执行指令**（包含该读哪些文件、要输出什么）
- `git-commit.md` 甚至写明了 Story ID 从分支名提取逻辑，异常场景处理（推送被拒绝/有冲突等）

**建议**：AIES 继承这 5 个模板作为默认模板库。

---

### ⭐ 5. 多平台入口桥接设计

- `CLAUDE.md` → Claude Code 入口
- `AGENTS.md` → Codex / 通用 Agent 入口（含 Trellis 引用）
- `.codebuddy/rules/*.md` → CodeBuddy 自动加载
- `.cursor/commands/*.md` → Cursor 自定义命令

**做得好的点**：同一份规范内容在多个平台生效，不做重复。

**小瑕疵**：`Rule.md`、`CLAUDE.md`、`.codebuddy/rules/ai-collaborative-development.md` 有内容重复，维护时可能不同步。

---

### ⭐ 6. Trellis 多 Agent 流水线的思考

虽然不一定人人需要，但 `.claude/agents/` 下的 6 个 Agent 定义（dispatch/research/plan/implement/check/debug）+ Hooks（session-start / inject-subagent-context / ralph-loop）展示了一个**可工作**的多 Agent 流水线。

**做得好的点**：
- Hook 自动注入 context 到 subagent，subagent 定义保持简洁
- `ralph-loop` 机制让 check agent 在问题未修完时不能退出
- `AGENTS_NO_PHASE_UPDATE = {"debug", "research"}` 区分了"会推进任务阶段"vs"临时调用"的 Agent

**建议**：AIES 作为 **Stage 4 可选模块**提供，默认不启用（见 `multi-agent-decision.md`）。

---

### ⭐ 7. changelog.md 独立维护的 token 优化

将变更日志从 index.md 分离出来，避免每次加载项目地图都把几百条历史 diff 塞进 AI 上下文，这是很聪明的设计。

---

### ⭐ 8. Swagger 规范的"血的教训"沉淀

`Rule.md` 第十节「Swagger Response Data 防污染规则」非常典型：
- 问题：YApi 解析 `allOf` 的合并缺陷导致字段污染
- 解法：`swaggerignore:"true"` tag + 嵌套泛型语法
- 沉淀：6 条强制规则 + 3 条验证命令

**这就是维度 3 "Rule 保一致"的最佳实践**：发现坑 → 立即写入 Spec → AI 永不再踩。

---

## 三、不足的地方（迁移时需要改进）⚠️

### ⚠️ 1. 规范体系「四套并存」，维护成本高

目前项目有：
- `Rule.md`（根目录）
- `.codebuddy/rules/ai-collaborative-development.md`
- `.trellis/spec/backend/*.md`
- `CLAUDE.md`

**问题**：
- `Rule.md` 和 `.codebuddy/rules/` 的内容重叠率 >60%
- 修改一个规则需要同步多份文件（容易不一致）
- 新人不知道该看哪份

**迁移方案**：
```
单一真相源：.aies/spec/
├── index.md
├── architecture.md        ← 架构约束
├── code-style.md          ← 代码风格
├── quality-gates.md       ← 质量门
└── error-handling.md

入口文件只做引用：
- CLAUDE.md    → "See .aies/spec/"
- AGENTS.md    → "See .aies/spec/"
- .cursorrules → "See .aies/spec/"
```

---

### ⚠️ 2. `.ai/` 和 `.trellis/spec/` 职责重叠

目前 `.ai/` 和 `.trellis/spec/` 都在存"规范类文档"：

| `.ai/` 内容 | `.trellis/spec/` 内容 |
|------------|---------------------|
| index.md（项目地图） | directory-structure.md（目录结构） |
| review-checklist.md | quality-guidelines.md |
| context-guide.md | index.md（导航） |

**问题**：职责定位不清晰，同一类内容在两处。

**迁移方案（AIES 统一设计）**：
```
.ai/           ← 项目实例信息（index/changelog/glossary/prompts）
.aies/spec/    ← 方法论与规范（code-style/architecture/quality-gates）
```
- `.ai/` 每个项目**不一样**（地图、术语、变更）
- `.aies/spec/` 各项目**大同小异**（可跨项目复用）

---

### ⚠️ 3. Trellis 脚本对 Python 3 依赖

`.trellis/scripts/` 全部用 Python 3 编写（get_context.py / add_session.py / task.py）。

**问题**：
- 前端项目（纯 Node/TS）不必装 Python 仅为跑脚本
- 部分团队环境 Python 版本不一致

**迁移方案**：
- AIES 提供 Python + Node.js **双版本**脚本
- 或合并到单一 `aies` CLI（Node.js 写，一次性安装）

---

### ⚠️ 4. 任务-Commit 关联是手工填写

`task.json` 的 `commit` 字段需要人手动填，`after_finish` hook 未启用。

**改进方向**：
```yaml
# .aies/config.yaml
hooks:
  after_finish:
    - "git rev-parse HEAD | xargs -I{} jq '.commit=\"{}\"' task.json > task.json.tmp && mv task.json.tmp task.json"
```

---

### ⚠️ 5. 会话日志记录是纯手动触发

会话结束后需要手动执行 `add_session.py`，容易遗忘。

**改进方向**：
- 在 Claude Code 的 `Stop` Hook 中触发
- 在 CodeBuddy 的完成清单 SOP 中强制提醒
- 提供 IDE 面板按钮（Cursor/VSCode 插件）

---

### ⚠️ 6. AI 盲区清单尚未完全项目化

`.ai/review-checklist.md` 通用性强，但项目独有的盲区（如 `MCP/Skill 删除未清理关联表`）分散在多处（Rule.md "已知待改进项"、changelog、Spec）。

**改进方向**：
- `.ai/known-issues.md` 专门收录项目的已知技术债
- AI 在生成相关模块代码时必须引用并提醒

---

### ⚠️ 7. 多 Agent 流水线上得太早（对单人项目）

`.claude/agents/` 下 6 个 Agent 定义 + Hooks + Ralph Loop 机制对**单人业务后端**来说是过度设计。

**观察**：
- `.trellis/tasks/` 下只有 4 个任务目录（说明使用频率不高）
- Multi-agent 脚本没有被高频使用

**建议**：
- 小项目退回 Stage 2（单 Agent + Spec + journal）
- 大项目保留，但 AIES 脚手架将其作为**可选 add-on**

---

### ⚠️ 8. 没有 CI 层的 AI Review 兜底

所有质量把控依赖 AI 自检 + 人工 review-checklist。CI 层只有基础编译，没有 AI 驱动的审查。

**改进方向**：
- GitHub Actions / 蓝盾 CI 增加 AI Review 步骤
- 每个 PR 自动跑 `review-checklist.md` 的所有检查项
- 失败阻断合并

---

### ⚠️ 9. Glossary（业务术语表）缺失

`Rule.md` 提到「业务术语表 — Agent/Skill/MCP Server 等 7 个核心术语定义」，但实际没有独立文件。术语散落在 Rule.md 和 spec 中。

**改进方向**：
- `.ai/glossary.md` 集中定义业务术语
- AI 每次加载 spec 时同时加载 glossary

---

### ⚠️ 10. 规范自身没有版本号和生效日期

所有 spec 文档用「最后更新 XXXX-XX-XX」，但没有版本号（v1.2.3 / v2.0.0），大改时难以 track。

**改进方向**：
```markdown
---
version: 1.3.0
updated: 2026-04-24
owner: {your-name}
---
```

---

## 四、得失总结表

| 维度 | 做得好 | 不足 |
|------|--------|------|
| 规范先行 | ⭐⭐⭐⭐⭐ 规则到可执行级别 | 四份规范重复 |
| 代码给 AI 读 | ⭐⭐⭐⭐⭐ 结构化注释、Swagger | — |
| Rule 保一致 | ⭐⭐⭐⭐⭐ Phase 1/2/3 协议 | 多平台分散 |
| 索引自维护 | ⭐⭐⭐⭐⭐ index.md 堪称典范 | changelog 略长 |
| 可追溯性 | ⭐⭐⭐⭐ [ai-assisted] 标记 | task-commit 未自动化 |
| 上下文管理 | ⭐⭐⭐⭐ context-guide.md 分场景 | 重复内容占上下文 |
| 隐性技术债 | ⭐⭐⭐⭐ 已知问题列表 | 未独立成档 |
| Prompt 资产化 | ⭐⭐⭐⭐⭐ 5 个实战模板 | 缺 refactor 模板 |

---

## 五、推荐的迁移策略（用 AIES 重构）

### Step 1：合并规范到 .aies/spec/

```bash
# 统一规范
mkdir -p .aies/spec
mv .trellis/spec/backend/* .aies/spec/
mv .trellis/spec/guides .aies/spec/

# 合并 Rule.md + CodeBuddy rules 的非重复内容
# Rule.md 保留为项目介绍 + 架构图
# .codebuddy/rules/ 改为单行引用：@.aies/spec/
```

### Step 2：精简各平台入口文件

```markdown
# CLAUDE.md（新版）
# agent-manage-backend — AI 规范

请严格遵循以下文件：
- `.aies/spec/index.md` —— 所有 Spec 的导航入口
- `.ai/index.md` —— 本项目地图与路由表
- `.ai/review-checklist.md` —— 代码审查清单

每次对话按 `.aies/workflow.md` 启动流程执行。
```

### Step 3：迁移 Trellis 到 .aies/

- `.trellis/tasks/` → `.aies/tasks/`
- `.trellis/workspace/` → `.aies/workspace/`
- `.trellis/scripts/` → `.aies/scripts/`（顺便拆分出 Node.js 版）
- `.trellis/workflow.md` → `.aies/workflow.md`

### Step 4：保留 `.claude/agents/` 作为可选流水线

- 改为从 `.aies/spec/` 读取规范（不再引用 `.trellis/`）
- AIES 默认不启用，在 Stage 4 用户主动启用

### Step 5：补齐缺失能力

- 新增 `.ai/glossary.md`（业务术语表）
- 新增 `.ai/known-issues.md`（项目已知技术债）
- 新增 `ci/github-actions/ai-review.yml`（CI 兜底）
- 给所有 Spec 加 frontmatter version

---

## 六、一句话点评

> **`agent-manage-backend` 是我见过**最成熟的全 AI 开发工程实践之一**，维度 1/2/3/4/8 都做到了 4 星以上。**
> **主要问题是「规范体系碎片化」和「多 Agent 上得早」，通过 AIES 脚手架的统一结构，可以用 1-2 天完成迁移，显著降低维护成本。**
